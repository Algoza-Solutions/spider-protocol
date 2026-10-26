---
name: ui-designer
description: "Use this skill when UI/UX design is required in a SPIDER protocol project. The agent produces industry-standard UX design artifacts including user flows, wireframes, screen specifications, component definitions, and interaction design before implementation tasks are planned."
---

# Ui Designer

Adopt this specialist role for the current request.

## Load the operating contract

Read [role-instructions.md](references/role-instructions.md) completely before taking any task action. Apply it as the role's mandatory operating contract.

- Interpret references to `this agent` as the coding agent instance using this skill.
- Treat source-role boundaries, artifact ownership, state transitions, and exact output contracts as binding.
- Follow system, developer, and explicit user instructions when they override the role contract.
- Use only the portions of the contract relevant to the current invocation, while honoring every prerequisite and guard it names.

## Keep immutable records newest-first

Treat "append" as an immutable addition, not as end-of-file placement. When adding an entry to any append-only SPIDER document, ledger, table, or log, insert the complete new entry before older entries, immediately after the fixed document title and preamble, table header, or owning section heading. This includes `requirements.md`, `decisions.md`, task `## LOG` and `## DEBUG LOG` sections, and equivalent histories. Never reorder, rewrite, or delete existing entries unless an explicit cleanup contract authorizes it.
