# Architecture — SPIDER Agent Workflow Protocol

## System Shape

SPIDER is a file-based governance and coordination protocol for AI coding agents. Instead of relying on transient chat memory or letting a single coding agent make silent architectural leaps, SPIDER splits software delivery across specialized roles that communicate through durable, repository-tracked Markdown and YAML contracts.

The protocol has four canonical layers in any adopting repository:

1. **Role contracts** installed as agent skills (`skills/<role>/`) or Claude Code agents (`agents/<role>.md`).
2. **Shared state artifacts** at the repository root: `requirements.md`, `project.md`, `decisions.md`, `architecture/architecture.md`, and `task-index.yaml`.
3. **Feature artifacts** under `features/<slug>/` (`requirements.md`, `build-plan.md`, `blast-radius-summary.md`, `design.html`, `tasks/`, `validation/`, `defects/`).
4. **Cryptographic bundle verification** (`skills/spider-orchestrator/scripts/verify_specialist_skills.py`) ensuring specialist role contracts have not drifted or been tampered with.

## Agent Responsibilities

| Role | Owns | Must Not Own |
| --- | --- | --- |
| `spider-orchestrator` / `orchestrator` | Conversational preflight discovery, minimum-baseline confirmation, `REQ-N` capture and lifecycle, coarse triage, exact-pointer routing, repair loop continuation, and user checkpoints. | Implementation, task creation, validation, architecture, or UI design. |
| `architect` | Deep impact triage, plan-freshness assessment, UI-need assessment, component boundaries, public APIs, cross-component data shapes, external dependencies, durable decisions (`decisions.md`), build plans, and blast-radius summaries. | Internal task implementation design, task documents, implementation, validation. |
| `ui-designer` | Feature UX specs and interaction contracts (`features/<slug>/design.html`). | Backend architecture, task planning, implementation. |
| `planner` | Minimum-sufficient implementation design under KISS, cohesive task decomposition, internal structure and wiring, test strategy, typed resumable `STEPS`, project task table, and `task-index.yaml`. | Silently changing architect-owned boundaries, writing production code, validation. |
| `task-executor` | Implementing one exact dispatched task (`Pending -> Active -> Ready for validation`) inside its authorized implementation shape. | Public contracts, scope expansion, new libraries, new tasks, architecture, or marking a task `Done`. |
| `task-validator` | Full contract-chain verification (REQ, GOAL, typed STEPS, behavior, task-scoped diff, upstream contracts, and project regression suite) and sole authority to mark a task `Done`. | Implementation fixes, architecture changes, task creation, requirement changes. |
| `debugger` | Reproduction, isolation, root-cause analysis, durable defect records (`features/<slug>/defects/`), and localized authorized fixes for `Blocked` tasks. | New features, unauthorized remediation scope, broad refactors, decisions, task creation. |
| `doc-cleanup` | Pruning and compacting completed SPIDER documentation while preserving immutable decision history and task-ID tombstones. | Source code, architecture decisions, validation. |

## Core Protocol Invariants

### 1. Preflight & Minimum-Change Authorization
Every worktree-changing request starts with an orchestrator conversational preflight before any SPIDER artifact is written. The orchestrator identifies the **direct baseline** (the smallest change using existing code, files, and structures) and explicitly discloses any proposed new production file, helper, class, service, layer, or dependency. Specialist reasoning cannot substitute for explicit user approval.

### 2. Peer Challenge Between Planner and Architect (KISS)
Architect and Planner are peers with distinct decision rights: Architect owns system boundaries; Planner owns the simplest code and task design inside those boundaries. If an architect boundary introduces unnecessary complexity without explicit REQ authorization, Planner challenges the boundary with a simpler direct alternative before creating tasks.

### 3. Single Active Delivery Slot & Exact Task Pointers
At most one task in a repository may be `Active` or `Ready for validation` at any time. Every dispatch and handoff carries the exact `requirement_id`, `task_id`, and `task_file`—downstream agents never guess "the next task."

### 4. Independent Validator & Regression Gate
`task-executor` can only move a task to `Ready for validation`. Only `task-validator` can mark a task `Done` after verifying:
- Every acceptance criterion and task `GOAL`
- Every typed `STEP` (`[create]`, `[modify]`, `[delete]`, `[reference]`, `[run]`) and the git diff against authorized mutation paths (ensuring read-only `[reference]` paths and out-of-scope files were not modified)
- Upstream compliance (`decisions.md`, `architecture.md`, `build-plan.md`, `design.html`, `blast-radius-summary.md`)
- Full project regression suite execution on the final task of a requirement

### 5. Newest-First Append-Only Ledgers & ISO 8601 Timestamps
All append-only SPIDER logs (`requirements.md`, `decisions.md`, task `## LOG`, and `## DEBUG LOG`) insert new entries newest-first immediately below the section header, stamped with second-precision timezone-qualified ISO 8601 timestamps (`YYYY-MM-DDTHH:mm:ss±HH:mm` or `Z`).
