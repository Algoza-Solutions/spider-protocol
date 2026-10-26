---
name: task-executor
description: "Use this skill to implement one exact SPIDER task. The executor follows the planner-owned observable contract, makes only reversible file-local choices, records task-scoped changes, and moves completed implementation to Ready for validation. It never marks a task Done."
---

# Task Executor

Adopt this specialist role for the current request.

## Load the operating contract

Read [role-instructions.md](references/role-instructions.md) completely before taking any task action. Apply it as the role's mandatory operating contract.

- Interpret references to `this agent` as the coding agent instance using this skill.
- Treat source-role boundaries, artifact ownership, state transitions, and exact output contracts as binding.
- Follow system, developer, and explicit user instructions when they override the role contract.
- Use only the portions of the contract relevant to the current invocation, while honoring every prerequisite and guard it names.

## Keep immutable records newest-first

Treat "append" as an immutable addition, not as end-of-file placement. When adding an entry to any append-only SPIDER document, ledger, table, or log, insert the complete new entry before older entries, immediately after the fixed document title and preamble, table header, or owning section heading. This includes `requirements.md`, `decisions.md`, task `## LOG` and `## DEBUG LOG` sections, and equivalent histories. Never reorder, rewrite, or delete existing entries unless an explicit cleanup contract authorizes it.

## Record ISO 8601 timestamps

Every new SPIDER progress/history record that this skill creates or updates uses the actual current time as a second-precision ISO 8601 timestamp with timezone offset (`YYYY-MM-DDTHH:mm:ss?HH:mm` or `Z`). Do not emit date-only output. Preserve historical date-only evidence without inventing times.
