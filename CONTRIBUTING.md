# Contributing to SPIDER Protocol

Thank you for your interest in improving the **SPIDER Agent Workflow Protocol**!

## Repository Structure

- `skills/` — The 8 packaged agent skills (`spider-orchestrator`, `architect`, `ui-designer`, `planner`, `task-executor`, `task-validator`, `debugger`, `doc-cleanup`) compatible with Codex, OpenCode, Gemini/Antigravity, and other `SKILL.md`-compatible coding environments.
- `agents/` — Single-file role contracts (`*.md`) formatted for Claude Code (`~/.claude/agents`).
- `template/` — Starter state stores copied into adopting repositories via `python scripts/install.py --init-project <dir>`.
- `docs/` — Protocol architecture, routing/repair flows, and terminology reference.

## Updating Specialist Role Contracts

Every specialist skill under `skills/<role>/` is cryptographically verified by `skills/spider-orchestrator/scripts/verify_specialist_skills.py` against `skills/spider-orchestrator/references/specialist-skill-manifest.json` using line-ending-normalized SHA-256 digests.

When you modify any file inside `skills/<role>/`:

1. Keep the corresponding Claude Code contract in `agents/<role>.md` synchronized.
2. Recompute the SHA-256 digest in `skills/spider-orchestrator/references/specialist-skill-manifest.json` (normalized with `\n` line endings, uppercase hex).
3. Run the verifier and the 22-test suite before opening a pull request:

```bash
python skills/spider-orchestrator/scripts/verify_specialist_skills.py --codex-home .
python -m unittest discover -s skills/spider-orchestrator/scripts -v
```

## Design Principles for Protocol Changes

- **Minimum-Change Discipline:** Do not add new protocol artifacts, states, or handoff fields when existing contracts can carry the required signal.
- **Role Separation:** Never blur the boundary between planning, execution, and validation (`task-validator` alone marks delivery tasks `Done`).
- **Portability:** Keep prompt contracts self-contained and free of host-specific paths or hardcoded personal configurations.
