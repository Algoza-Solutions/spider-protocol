#!/usr/bin/env python3
"""Cross-platform installer and project initializer for the SPIDER Protocol."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_SRC = REPO_ROOT / "skills"
AGENTS_SRC = REPO_ROOT / "agents"
TEMPLATE_SRC = REPO_ROOT / "template"

SKILL_ROLES = (
    "spider-orchestrator",
    "architect",
    "ui-designer",
    "planner",
    "task-executor",
    "task-validator",
    "debugger",
    "doc-cleanup",
)

AGENT_FILES = (
    "orchestrator.md",
    "architect.md",
    "ui-designer.md",
    "planner.md",
    "task-executor.md",
    "task-validator.md",
    "debugger.md",
    "doc-cleanup.md",
)


def default_target_roots() -> dict[str, Path]:
    home = Path.home()
    codex_home = Path(os.environ["CODEX_HOME"]).expanduser() if os.environ.get("CODEX_HOME") else home / ".codex"
    return {
        "codex": codex_home / "skills",
        "opencode": home / ".config" / "opencode" / "skills",
        "gemini": home / ".gemini" / "config" / "skills",
        "claude": home / ".claude" / "agents",
    }


def install_skills(dest_skills_dir: Path) -> None:
    dest_skills_dir = dest_skills_dir.expanduser().resolve()
    dest_skills_dir.mkdir(parents=True, exist_ok=True)
    for role in SKILL_ROLES:
        src = SKILLS_SRC / role
        dst = dest_skills_dir / role
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    print(f"[OK] Installed 8 SPIDER skills -> {dest_skills_dir}")

    verifier = dest_skills_dir / "spider-orchestrator" / "scripts" / "verify_specialist_skills.py"
    parent_home = dest_skills_dir.parent
    result = subprocess.run(
        [sys.executable, "-B", str(verifier), "--codex-home", str(parent_home)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(f"[ERROR] Bundle verification failed for {dest_skills_dir}:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
        sys.exit(result.returncode)
    print(f"[OK] Verified specialist skill manifest (SHA-256) in {dest_skills_dir}")


def install_claude_agents(dest_agents_dir: Path) -> None:
    dest_agents_dir = dest_agents_dir.expanduser().resolve()
    dest_agents_dir.mkdir(parents=True, exist_ok=True)
    for filename in AGENT_FILES:
        src = AGENTS_SRC / filename
        dst = dest_agents_dir / filename
        shutil.copy2(src, dst)
    print(f"[OK] Installed 8 SPIDER Claude Code agents -> {dest_agents_dir}")


def init_project(project_dir: Path, *, force: bool = False) -> None:
    project_dir = project_dir.expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    created, skipped = [], []
    for item in TEMPLATE_SRC.rglob("*"):
        rel = item.relative_to(TEMPLATE_SRC)
        target = project_dir / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            skipped.append(str(rel))
        else:
            shutil.copy2(item, target)
            created.append(str(rel))
    if created:
        print(f"[OK] Initialized SPIDER template in {project_dir}: {', '.join(created)}")
    if skipped:
        print(f"[SKIP] Preserved existing files in {project_dir} (use --force to overwrite): {', '.join(skipped)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install SPIDER Protocol skills/agents and initialize project state stores."
    )
    parser.add_argument(
        "--target",
        choices=("codex", "opencode", "gemini", "claude", "all"),
        help="Install into the standard user directory for Codex, OpenCode, Gemini/Antigravity, Claude Code, or all four.",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        help="Custom destination directory for the 8 SPIDER skill folders (must end in '/skills' for verifier compatibility).",
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        help="Custom destination directory for the 8 Claude Code agent Markdown files.",
    )
    parser.add_argument(
        "--init-project",
        type=Path,
        metavar="PROJECT_DIR",
        help="Copy starter SPIDER state files (project.md, requirements.md, decisions.md, task-index.yaml, architecture/, features/) into PROJECT_DIR.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files when running --init-project.",
    )

    args = parser.parse_args()
    if not (args.target or args.skills_dir or args.agents_dir or args.init_project):
        parser.print_help()
        return 1

    roots = default_target_roots()

    if args.target in ("codex", "all"):
        install_skills(roots["codex"])
    if args.target in ("opencode", "all"):
        install_skills(roots["opencode"])
    if args.target in ("gemini", "all"):
        install_skills(roots["gemini"])
    if args.target in ("claude", "all"):
        install_claude_agents(roots["claude"])

    if args.skills_dir:
        install_skills(args.skills_dir)
    if args.agents_dir:
        install_claude_agents(args.agents_dir)
    if args.init_project:
        init_project(args.init_project, force=args.force)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
