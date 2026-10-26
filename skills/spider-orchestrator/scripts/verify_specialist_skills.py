#!/usr/bin/env python3
"""Verify that SPIDER specialist skills match reviewed contracts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = SKILL_ROOT / "references" / "specialist-skill-manifest.json"
SUPPORTED_VERSION = 3
REQUIRED_SPECIALISTS = frozenset({
    "architect", "ui-designer", "planner", "task-executor",
    "task-validator", "debugger", "doc-cleanup",
})
REQUIRED_FILES = frozenset({"SKILL.md", "references/role-instructions.md", "agents/openai.yaml"})


def sha256(path: Path) -> str:
    """Hash reviewed text with platform-independent line endings."""

    digest = hashlib.sha256()
    content = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    digest.update(content)
    return digest.hexdigest().upper()


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def frontmatter_name(skill_md: Path) -> str | None:
    """Read the bundle's supported single-line name/description scalars."""
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---[ \t]*\n(?P<body>.*?)\n---[ \t]*(?:\n|$)", text, re.DOTALL)
    if not match:
        return None
    fields = {}
    for key in ("name", "description"):
        values = re.findall(rf"^{key}:[ \t]*([^\n]*)$", match.group("body"), re.MULTILINE)
        if len(values) != 1:
            return None
        value = values[0].strip()
        if value.startswith('"'):
            quoted = re.fullmatch(r'("(?:[^"\\]|\\.)*")(?:[ \t]+#.*)?', value)
            if not quoted:
                return None
            try:
                value = json.loads(quoted.group(1))
            except ValueError:
                return None
        elif value.startswith("'"):
            quoted = re.fullmatch(r"('(?:[^']|'')*')(?:[ \t]+#.*)?", value)
            if not quoted:
                return None
            value = quoted.group(1)[1:-1].replace("''", "'")
        else:
            value = re.split(r"[ \t]+#", value, maxsplit=1)[0].strip()
            if (not value or value[0] in "#[]{}|>&*!@`%"
                    or value.startswith(("- ", "? ", ": ")) or re.search(r":[ \t]", value)
                    or value.lower() in {"null", "~", "true", "false", "yes", "no", "on", "off"}
                    or re.fullmatch(
                        r"[-+]?(?:(?:[0-9][0-9_]*(?:\.[0-9_]*)?|\.[0-9]+)(?:e[-+]?[0-9]+)?"
                        r"|\.inf|\.nan|0[box][0-9a-f_]+)", value, re.I
                    )):
                return None
        if not isinstance(value, str) or not value.strip():
            return None
        fields[key] = value.strip()
    return fields["name"]


def verify_skill(name: str, spec: dict[str, object], skills_dir: Path) -> dict[str, object]:
    skill_dir = skills_dir / spec["directory"]
    result: dict[str, object] = {
        "name": name,
        "path": str(skill_dir),
        "exists": False,
        "contract_valid": False,
        "files": [],
        "errors": [],
    }
    errors = result["errors"]
    files = result["files"]
    assert isinstance(errors, list)
    assert isinstance(files, list)

    try:
        result["exists"] = skill_dir.is_dir()
    except OSError as exc:
        errors.append(f"cannot read skill directory: {exc}")
        return result
    if not result["exists"]:
        errors.append("skill directory is missing")
        return result

    for relative, expected in spec["files"].items():
        path = skill_dir / relative
        file_result = {
            "path": str(path),
            "exists": False,
            "expected_sha256": expected.upper(),
            "actual_sha256": None,
        }
        try:
            file_result["exists"] = path.is_file()
            if not file_result["exists"]:
                errors.append(f"missing file: {relative}")
            else:
                path.read_text(encoding="utf-8")
                actual = sha256(path)
                file_result["actual_sha256"] = actual
                if actual != file_result["expected_sha256"]:
                    errors.append(f"SHA-256 mismatch: {relative}")
                if relative == "SKILL.md" and frontmatter_name(path) != name:
                    errors.append("SKILL.md frontmatter is invalid or has the wrong name")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read {relative}: {exc}")
        files.append(file_result)

    result["contract_valid"] = not errors
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify specialist skills used by the spider-orchestrator skill."
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=default_codex_home(),
        help="Codex home containing skills/ (default: CODEX_HOME or ~/.codex)",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Reviewed specialist-skill manifest bundled with the orchestrator",
    )
    args = parser.parse_args()

    try:
        manifest_path = args.manifest.resolve()
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest must be an object")
        if type(manifest.get("version")) is not int or manifest["version"] != SUPPORTED_VERSION:
            raise ValueError(f"manifest version must be integer {SUPPORTED_VERSION}")
        specialists = manifest.get("specialists")
        if not isinstance(specialists, dict) or set(specialists) != REQUIRED_SPECIALISTS:
            raise ValueError("specialists must contain exactly: " + ", ".join(sorted(REQUIRED_SPECIALISTS)))
        for name, spec in specialists.items():
            if not isinstance(spec, dict) or spec.get("directory") != name:
                raise ValueError(f"{name}: specification must be an object with directory equal to its role name")
            file_specs = spec.get("files")
            if not isinstance(file_specs, dict) or set(file_specs) != REQUIRED_FILES:
                raise ValueError(f"{name}: files must contain exactly: " + ", ".join(sorted(REQUIRED_FILES)))
            for relative, digest in file_specs.items():
                if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                    raise ValueError(f"{name}/{relative}: SHA-256 must be a 64-character hexadecimal string")
    except Exception as exc:  # noqa: BLE001 - verifier must fail closed
        print(json.dumps({"ok": False, "manifest": str(args.manifest), "error": str(exc)}, indent=2))
        return 2

    try:
        codex_home = args.codex_home.expanduser().resolve()
    except (OSError, RuntimeError) as exc:
        codex_home = args.codex_home
        results = [
            {
                "name": name,
                "path": str(codex_home / "skills" / spec["directory"]),
                "exists": False,
                "contract_valid": False,
                "files": [],
                "errors": [f"cannot resolve Codex home: {exc}"],
            }
            for name, spec in specialists.items()
        ]
    else:
        results = [
            verify_skill(name, spec, codex_home / "skills")
            for name, spec in specialists.items()
        ]
    ok = all(item["contract_valid"] for item in results)
    print(
        json.dumps(
            {
                "ok": ok,
                "codex_home": str(codex_home),
                "manifest": str(manifest_path),
                "specialists": results,
            },
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
