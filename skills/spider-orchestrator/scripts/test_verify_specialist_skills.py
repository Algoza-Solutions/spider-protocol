"""Behavioral regression tests for the specialist bundle verifier CLI."""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name("verify_specialist_skills.py").resolve()
ROLES = ("architect", "ui-designer", "planner", "task-executor",
         "task-validator", "debugger", "doc-cleanup")
FILES = ("SKILL.md", "references/role-instructions.md", "agents/openai.yaml")
MODULE_SPEC = importlib.util.spec_from_file_location("bundle_verifier", SCRIPT)
VERIFIER = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(VERIFIER)


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="spider verifier ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.codex_home = self.root / "fake codex home"
        self.manifest_path = self.root / "manifest.json"
        self.manifest = {"version": 3, "specialists": {}}
        for role in ROLES:
            hashes = {}
            for relative in FILES:
                content = (f"---\nname: {role}\ndescription: Review the {role} contract.\n---\nBody.\n"
                           if relative == "SKILL.md" else f"Reviewed {role} {relative}\n")
                path = self.codex_home / "skills" / role / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content.encode("utf-8"))
                hashes[relative] = hashlib.sha256(content.encode("utf-8")).hexdigest().upper()
            self.manifest["specialists"][role] = {"directory": role, "files": hashes}
        self.save_manifest()

    def save_manifest(self, manifest=None):
        self.manifest_path.write_text(
            json.dumps(self.manifest if manifest is None else manifest), encoding="utf-8"
        )

    def cli(self, expected, *, args=None, cwd=None, env=None):
        if args is None:
            args = ["--codex-home", str(self.codex_home), "--manifest", str(self.manifest_path)]
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *args], cwd=cwd, env=env,
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, expected, (result.stdout + result.stderr)[-2500:])
        self.assertEqual(result.stderr, "")
        payload = json.loads(result.stdout)
        self.assertIs(payload["ok"], expected == 0)
        if expected == 2:
            self.assertTrue(payload["error"])
            self.assertNotIn("specialists", payload)
        return payload

    def rewrite_skill(self, content):
        path = self.codex_home / "skills/architect/SKILL.md"
        data = content.encode("utf-8") if isinstance(content, str) else content
        path.write_bytes(data)
        self.manifest["specialists"]["architect"]["files"]["SKILL.md"] = (
            hashlib.sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()
        )
        self.save_manifest()

    def assert_bundle_error(self, expected_text):
        payload = self.cli(1)
        role = next(item for item in payload["specialists"] if item["name"] == "architect")
        self.assertFalse(role["contract_valid"])
        self.assertIn(expected_text, " ".join(role["errors"]))
        self.assertTrue(all(item["contract_valid"] for item in payload["specialists"]
                            if item["name"] != "architect"))
        return role

    def test_complete_bundle_preserves_result_fields(self):
        payload = self.cli(0)
        self.assertEqual(set(payload), {"ok", "codex_home", "manifest", "specialists"})
        self.assertEqual(payload["codex_home"], str(self.codex_home.resolve()))
        self.assertEqual(payload["manifest"], str(self.manifest_path.resolve()))
        self.assertEqual({item["name"] for item in payload["specialists"]}, set(ROLES))
        for item in payload["specialists"]:
            self.assertEqual(set(item), {"name", "path", "exists", "contract_valid", "files", "errors"})
            self.assertTrue(item["exists"] and item["contract_valid"])
            self.assertEqual(item["errors"], [])
            self.assertEqual(len(item["files"]), 3)
            for file in item["files"]:
                self.assertEqual(set(file), {"path", "exists", "expected_sha256", "actual_sha256"})
                self.assertEqual(file["actual_sha256"], file["expected_sha256"])

    def test_line_endings_and_lowercase_digests(self):
        originals = {path: path.read_bytes() for path in (self.codex_home / "skills").rglob("*")
                     if path.is_file()}
        for newline in (b"\n", b"\r\n", b"\r"):
            with self.subTest(newline=newline):
                for path, data in originals.items():
                    path.write_bytes(data.replace(b"\n", newline))
                for spec in self.manifest["specialists"].values():
                    spec["files"] = {path: digest.lower() for path, digest in spec["files"].items()}
                self.save_manifest()
                self.cli(0)

    def test_extra_physical_files_and_manifest_metadata_are_allowed(self):
        (self.codex_home / "skills/architect/extra.txt").write_text("Unreviewed local note.")
        self.manifest["review_note"] = "metadata outside the required contract"
        self.save_manifest()
        self.cli(0)

    def test_manifest_file_failures(self):
        for data in (b"{bad json", b"\xff"):
            with self.subTest(data=data):
                self.manifest_path.write_bytes(data)
                self.cli(2)
        self.manifest_path.unlink()
        self.cli(2)

    def test_manifest_root_and_version_types(self):
        for root in ([], None, 3, "manifest", False):
            with self.subTest(root=root):
                self.save_manifest(root)
                # None is the helper's default; write JSON null explicitly.
                if root is None:
                    self.manifest_path.write_text("null")
                self.cli(2)
        for version in (None, False, True, 3.0, "3", 2, 999):
            with self.subTest(version=version):
                manifest = copy.deepcopy(self.manifest)
                manifest["version"] = version
                self.save_manifest(manifest)
                self.cli(2)
        manifest = copy.deepcopy(self.manifest)
        del manifest["version"]
        self.save_manifest(manifest)
        self.cli(2)

    def test_exact_specialist_membership(self):
        for value in (None, [], "architect", {}, 7):
            with self.subTest(value=value):
                self.save_manifest({"version": 3, "specialists": value})
                self.cli(2)
        self.save_manifest({"version": 3})
        self.cli(2)
        for role in ROLES:
            with self.subTest(missing=role):
                manifest = copy.deepcopy(self.manifest)
                del manifest["specialists"][role]
                self.save_manifest(manifest)
                self.cli(2)
        manifest = copy.deepcopy(self.manifest)
        manifest["specialists"]["extra"] = manifest["specialists"]["architect"]
        self.save_manifest(manifest)
        self.cli(2)

    def test_role_spec_and_directory_types(self):
        for value in (None, [], "architect", 7):
            with self.subTest(spec=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["specialists"]["architect"] = value
                self.save_manifest(manifest)
                self.cli(2)
        for value in (None, [], {}, 7, "planner", "../architect", ""):
            with self.subTest(directory=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["specialists"]["architect"]["directory"] = value
                self.save_manifest(manifest)
                self.cli(2)
        manifest = copy.deepcopy(self.manifest)
        del manifest["specialists"]["architect"]["directory"]
        self.save_manifest(manifest)
        self.cli(2)

    def test_exact_reviewed_file_map(self):
        for value in (None, [], "SKILL.md", {}, 7):
            with self.subTest(files=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["specialists"]["architect"]["files"] = value
                self.save_manifest(manifest)
                self.cli(2)
        for relative in (*FILES, "files"):
            with self.subTest(missing=relative):
                manifest = copy.deepcopy(self.manifest)
                spec = manifest["specialists"]["architect"]
                if relative == "files":
                    del spec["files"]
                else:
                    del spec["files"][relative]
                self.save_manifest(manifest)
                self.cli(2)
        manifest = copy.deepcopy(self.manifest)
        manifest["specialists"]["architect"]["files"]["extra.txt"] = "a" * 64
        self.save_manifest(manifest)
        self.cli(2)

    def test_digest_types_and_full_hex_length(self):
        for digest in (None, False, 123, [], {}, "", "a" * 63, "a" * 65,
                       "g" * 64, "a" * 64 + "\n", " " + "a" * 64):
            with self.subTest(digest=digest):
                manifest = copy.deepcopy(self.manifest)
                manifest["specialists"]["architect"]["files"]["SKILL.md"] = digest
                self.save_manifest(manifest)
                self.cli(2)

    def test_missing_skill_directory(self):
        (self.codex_home / "skills/architect").rename(self.root / "removed architect")
        self.assert_bundle_error("skill directory is missing")

    def test_missing_each_file_and_directory_instead_of_file(self):
        for relative in FILES:
            path = self.codex_home / "skills/architect" / relative
            data = path.read_bytes()
            with self.subTest(relative=relative):
                path.unlink()
                self.assert_bundle_error("missing file: " + relative)
                path.mkdir()
                self.assert_bundle_error("missing file: " + relative)
                path.rmdir()
                path.write_bytes(data)

    def test_hash_mismatch(self):
        path = self.codex_home / "skills/architect/references/role-instructions.md"
        path.write_bytes(b"Tampered contract\n")
        self.assert_bundle_error("SHA-256 mismatch")

    def test_invalid_frontmatter_with_matching_hash(self):
        cases = ["No frontmatter\n", "---\nname: planner\ndescription: Valid\n---\n",
                 "---\nname: architect\n---\n", "---\ndescription: Valid\n---\n",
                 "---\ndescription:\nname: architect\n---\n",
                 "---\nname:\ndescription: architect\n---\n"]
        for description in ("", " ", '""', "''", '"  "', "[]", "{}", "null",
                            "true", "42", "3.0", "1e3", ".5e+2", "0xFF", "- item", "# comment", "'unterminated"):
            cases.append(f"---\nname: architect\ndescription: {description}\n---\n")
        for content in cases:
            with self.subTest(content=content):
                self.rewrite_skill(content)
                role = self.assert_bundle_error("frontmatter")
                self.assertFalse(any("mismatch" in error for error in role["errors"]))

    def test_supported_nonempty_scalar_descriptions(self):
        for description in ('"Quoted description"', "'Single quoted description'", "A normal description.",
                            '"Review this project" # human note', "'Review this project' # human note",
                            "7 supported roles.", "-42 is a meaningful example."):
            with self.subTest(description=description):
                self.rewrite_skill(f"---\nname: 'architect'\ndescription: {description}\n---\n")
                self.cli(0)

    def test_invalid_utf8_in_reviewed_files(self):
        for relative in FILES:
            with self.subTest(relative=relative):
                path = self.codex_home / "skills/architect" / relative
                original = path.read_bytes()
                path.write_bytes(b"\xff")
                digest = self.manifest["specialists"]["architect"]["files"][relative]
                self.manifest["specialists"]["architect"]["files"][relative] = hashlib.sha256(b"\xff").hexdigest()
                self.save_manifest()
                self.assert_bundle_error("read")
                path.write_bytes(original)
                self.manifest["specialists"]["architect"]["files"][relative] = digest

    def test_relative_paths_and_codex_home_environment(self):
        self.cli(0, args=["--codex-home", self.codex_home.name, "--manifest", self.manifest_path.name], cwd=self.root)
        env = dict(os.environ, CODEX_HOME=str(self.codex_home))
        self.cli(0, args=["--manifest", str(self.manifest_path)], cwd=self.root, env=env)
        self.cli(0, cwd=self.root, env=dict(env, CODEX_HOME=str(self.root / "wrong")))

    def test_default_manifest_is_relative_to_script(self):
        repository = SCRIPT.parents[3]
        self.cli(0, args=["--codex-home", str(repository)], cwd=self.root)

    def test_default_home_without_environment(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, "home", return_value=self.root):
            self.assertEqual(VERIFIER.default_codex_home(), self.root / ".codex")

    def test_manifest_is_checked_before_bundle_reads(self):
        self.manifest["version"] = 999
        self.save_manifest()
        output = io.StringIO()
        with patch.object(sys, "argv", [str(SCRIPT), "--manifest", str(self.manifest_path)]), \
                patch.object(VERIFIER, "verify_skill", side_effect=AssertionError("bundle read")), \
                contextlib.redirect_stdout(output):
            self.assertEqual(VERIFIER.main(), 2)
        self.assertFalse(json.loads(output.getvalue())["ok"])

    def test_read_failures_stay_structured(self):
        target = (self.codex_home / "skills/architect/SKILL.md").resolve()
        original_read = Path.read_text
        def unreadable(path, *args, **kwargs):
            if path == target:
                raise PermissionError("simulated denied read")
            return original_read(path, *args, **kwargs)
        for mocked in (patch.object(VERIFIER, "sha256", side_effect=PermissionError("denied hash")),
                       patch.object(VERIFIER, "frontmatter_name", side_effect=PermissionError("denied frontmatter")),
                       patch.object(Path, "read_text", unreadable)):
            with self.subTest(mocked=mocked), mocked, \
                    patch.object(sys, "argv", [str(SCRIPT), "--codex-home", str(self.codex_home),
                                              "--manifest", str(self.manifest_path)]):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(VERIFIER.main(), 1)
                payload = json.loads(output.getvalue())
                self.assertFalse(payload["ok"])
                self.assertTrue(payload["specialists"][0]["errors"])

    def test_path_resolution_failures_stay_structured(self):
        original_resolve = Path.resolve
        for target, expected in ((self.codex_home, 1), (self.manifest_path, 2)):
            def denied(path, *args, **kwargs):
                if path == target:
                    raise PermissionError("simulated resolution failure")
                return original_resolve(path, *args, **kwargs)
            with self.subTest(target=target), patch.object(Path, "resolve", denied), \
                    patch.object(sys, "argv", [str(SCRIPT), "--codex-home", str(self.codex_home),
                                              "--manifest", str(self.manifest_path)]):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertEqual(VERIFIER.main(), expected)
                payload = json.loads(output.getvalue())
                self.assertFalse(payload["ok"])
                if expected == 1:
                    self.assertEqual(len(payload["specialists"]), 7)
                    self.assertTrue(all(not item["contract_valid"] and item["errors"]
                                        for item in payload["specialists"]))
                else:
                    self.assertTrue(payload["error"])

    def test_help_keeps_argparse_behavior(self):
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--codex-home", result.stdout)
        self.assertIn("--manifest", result.stdout)


if __name__ == "__main__":
    unittest.main()
