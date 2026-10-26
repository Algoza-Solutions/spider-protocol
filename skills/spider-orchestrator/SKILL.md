---
name: spider-orchestrator
description: "Coordinate software delivery in repositories that use the SPIDER protocol. Use when the coding agent must act as the SPIDER orchestrator: investigate and clarify a new change request conversationally before documentation or routing, write a free-form detailed requirements file plus a minimal linked requirements.md entry after explicit user confirmation, route confirmed work through architect, ui-designer, planner, task-executor, task-validator, debugger, or doc-cleanup skills, resume an authorized task, manage repair loops, enforce one exact task at a time, or present decision and iteration checkpoints. Execute every role skill sequentially in the current thread; never launch subagents for SPIDER roles. Also use for SPIDER status or process questions and explicit commit management; do not use for unrelated repositories."
---

# SPIDER Orchestrator

Act as the protocol coordinator and first point of contact. Keep the human as the product decision-maker. Capture authorized intent, choose the minimal safe route, serialize exact-task delivery, keep in-scope repair loops moving, and return control at a defined checkpoint.

Before that existing SPIDER workflow begins for a new change request, run the conversational discovery preflight below. Treat the user's confirmed final proposal as the operative user request for every existing downstream contract.

While acting as orchestrator, do not implement product code, design UI, make architecture decisions, create tasks, investigate defects, or validate completion. Switch to the owning skill in the current thread before performing that work.

During preflight, perform read-only requirement discovery without assuming a specialist role.

Never spawn, launch, or delegate to a subagent for a SPIDER role. Run one role at a time in this thread by loading its named skill, adopting its boundary, completing its work, and then resuming orchestration from its handoff data.

## Load the contracts

- Read [requirements-and-checkpoints.md](references/requirements-and-checkpoints.md) completely before creating, amending, superseding, or closing a requirement, before presenting a checkpoint, or before routing a Done revalidation or legacy audit.
- Read [routing-and-handoffs.md](references/routing-and-handoffs.md) completely before changing roles, accepting handoff data, running a task, resuming a Blocked repair, or entering a repair loop.

## Resolve the project and roles

1. Resolve the project root with `git rev-parse --show-toplevel`; fall back to the current working directory when it is not a Git repository.
2. Resolve the skills root (parent directory of `skills/`): check `CODEX_HOME` (`<codex-root>/skills/`), `~/.codex/skills/`, `~/.config/opencode/skills/`, `~/.gemini/config/skills/`, or the directory containing this skill bundle.
3. Locate specialist skills under `<skills-root>/skills/`: `architect`, `ui-designer`, `planner`, `task-executor`, `task-validator`, `debugger`, and `doc-cleanup`.
4. Before the first specialist role transition in a session, run `python "<skills-root>/skills/spider-orchestrator/scripts/verify_specialist_skills.py" --codex-home "<skills-root>"` using the resolved skills root from step 2. Treat its manifest as the compatibility contract for this skill bundle.
5. If any specialist skill is missing, invalid, or hash-mismatched, stop at a decision checkpoint. Report the exact mismatch and re-sync the affected skill from the source bundle; do not silently use a stale contract or a broad fallback role.
6. Invoke a verified specialist by loading its `SKILL.md` and required references in the current thread, then apply that contract while preserving its ownership boundary. Do not call subagent, delegation, or collaboration tools for role execution.

Keep role-transition context minimal. Reconstruct role-specific context from canonical artifacts instead of relying on transient chat summaries.

## Preflight new change requests

Add this orchestrator-only phase before the existing SPIDER entry workflow. Do not alter any specialist's responsibilities, input contract, routing, state transition, or handoff because of this phase.

Treat a new bug report, issue, feature request, behavior change, refactor, maintenance change, or cleanup request as a request candidate until the user confirms its final meaning. Read-only questions, status checks, commit-only work over accepted changes, exact-task resumes or validation, and repairs inside an accepted requirement continue through their existing paths without a new preflight. Material ambiguity in a new request is resolved here, before any requirement exists.

Keep preflight free-flowing and documentation-free:

1. Do not create or amend a requirement, task, design, decision, report, or other SPIDER artifact.
2. Do not transition to another SPIDER role.
3. Inspect relevant code, tests, configuration, requirements, decisions, architecture, task history, and version history without changing the worktree. Locate applicable decisions and architecture sections by search rather than loading whole append-only logs.
4. Reconstruct current behavior, contracts, invariants, and why they exist. Separate facts, inferences, and unresolved questions.
5. Compare repository evidence with the user's mental model and desired outcome. Surface accidental invariant changes and unexpected scope.
6. Discuss narrower alternatives, prerequisites, reprioritization, deferral, or cancellation when useful. Present one cognitively useful decision at a time, asking the smallest question that resolves it.
7. Establish the direct implementation baseline: the smallest change using existing code, structures, conventions, and owners that can satisfy the request. Disclose every proposed new production file, helper, class, service, layer, dependency, framework, public contract, storage shape, runtime process, reusable abstraction, or comparable structural addition. When the baseline can satisfy the request, obtain explicit user approval before including the addition; specialist justification is not authorization.
8. Converge on the outcome, preserved or intentionally changed invariants, scope, non-goals, assumptions, acceptance outcomes, authorized implementation shape, and sequencing.
9. Present a concise final proposal that names the direct baseline and every proposed added structure, then ask the user to confirm, revise, defer, or cancel it.

If the user revises the proposal, continue preflight. If the user defers or cancels it, stop without documentation. If the user confirms it:

1. Treat the confirmed proposal as the user's operative request.
2. Write the complete requirement to a separate Markdown file at a stable repository-relative path. Follow an existing naming convention when available. Do not prescribe a template, fixed headings, ordering, or layout; structure the document for the requirement at hand. Preserve stable `AC-N` identifiers somewhere in its free-form content, together with the confirmed direct baseline and every explicitly approved structural addition. When none is approved, make the minimum-direct-change posture unambiguous without adding a fixed field or section.
3. Add a minimal `Ready` entry to `requirements.md` with the REQ ID, timestamp, lifecycle status, concise request, inline link to the detailed file, supersession pointer, one concise trace summary per `AC-N`, and validation-evidence placeholders. Do not duplicate the detailed narrative in the registry.
4. Continue immediately through the unchanged route-selection and handoff sequence. Include the detailed file as one of the existing one-line relevant-artifact pointers to the next role and state that the root entry plus linked file together are the exact `REQ-N` contract.

Before routing, verify that the inline link resolves to the file just written and that the handoff pointer names the same path. Do not request a second confirmation for the written version.

Scale the preflight to the evidence. A verified mechanical edit may need only one compact exchange, but it still passes through the same confirmation boundary.

## Start every request

1. Inspect the repository and working tree without changing them.
2. Check for the canonical SPIDER artifacts:
   - `project.md`
   - `requirements.md`
   - `decisions.md`
   - `architecture/architecture.md`
   - `task-index.yaml`
   - `features/`
3. Reconcile `task-index.yaml`, `project.md`, and the referenced task document before a task-role transition. Permit only one delivery-slot task: `Active` or `Ready for validation`.
4. Classify the request as direct/read-only, commit-only, worktree-changing, or a new request candidate that needs preflight.
5. For every worktree-changing request, identify one existing requirement or record one new stable `REQ-N` before routing. Treat documentation cleanup as worktree-changing.
6. State the chosen path and why in one concise update, then continue without a ceremonial confirmation when the request is clear.

Create and maintain `requirements.md`. Create a minimal `project.md` only when initializing a new SPIDER project. Do not fabricate missing architect-, designer-, planner-, executor-, debugger-, cleanup-, or validator-owned artifacts; route their creation or repair to the owning role.

## Keep immutable records newest-first

Treat "append" as an immutable addition, not as end-of-file placement. When adding an entry to any append-only SPIDER document, ledger, table, or log, insert the complete new entry before older entries, immediately after the fixed document title and preamble, table header, or owning section heading. This includes `requirements.md`, `decisions.md`, task `## LOG` and `## DEBUG LOG` sections, and equivalent histories. Never reorder, rewrite, or delete existing entries unless an explicit cleanup contract authorizes it.

## Record ISO 8601 timestamps

Every new SPIDER progress/history record that this skill creates or updates uses the actual current time as a second-precision ISO 8601 timestamp with timezone offset (`YYYY-MM-DDTHH:mm:ss?HH:mm` or `Z`). Do not emit date-only output. Preserve historical date-only evidence without inventing times.

## Bootstrap an incomplete SPIDER project

Do not run implementation until all required protocol artifacts exist and their state is coherent.

1. Create `requirements.md` and a minimal `project.md` when absent; capture the user's authorized request.
2. Route to architect to create or repair `decisions.md`, `architecture/architecture.md`, and the required plan or blast-radius artifacts.
3. Route through ui-designer when the architect sets `ui_design_needed: true`, then return to architect for design-readiness reconciliation before planner.
4. Route to planner to create or repair `task-index.yaml`, `features/`, and exact task documents.
5. Re-run the artifact and delivery-slot checks before transitioning to task-executor.

If a required owner cannot run, stop at a decision checkpoint instead of writing its artifact yourself.

## Handle direct requests

Handle a request directly only when it requires no specialist judgment or specialist-owned write. Direct handling includes:

- Answering questions about SPIDER, existing artifacts, or known project behavior
- Reading or summarizing project documents
- Checking repository or task status with read-only commands
- Explaining the next routed step
- Managing commits when the user explicitly requests commit management over accepted work

Do not capture a requirement for a read-only answer, status check, or commit-only operation over already accepted work.

## Capture authorized intent

For a new request, this section applies only after preflight confirmation. Treat the confirmed final proposal as the user's request and record it as `Ready`; never record a new request as `Draft`. Put the complete requirement in its separate free-form Markdown file. Keep only the minimal linked registry entry and acceptance/evidence trace in `requirements.md`, as defined in [requirements-and-checkpoints.md](references/requirements-and-checkpoints.md).

Return an `In Progress` requirement to `Draft` only when a specialist surfaces unresolved user intent; ask the smallest question that resolves it and do not transition to a specialist skill until it is `Ready` again.

Set the requirement to `In Progress` when transitioning to its first specialist skill or exact implementation task. Preserve stable IDs and append amendments; never silently rewrite accepted criteria. Do not reopen completed history for a regression or material follow-up.

## Choose the route

Evaluate special cases first:

- SPIDER/process/status/explicit commit request: handle directly.
- Documentation cleanup: capture a Ready requirement, then route to `doc-cleanup`.
- User-reported bug without an authorized task: capture a Ready requirement, then route to `debugger` in taskless diagnosis mode.
- Defect tied to the exact current Blocked task: route to `debugger` with the exact task pointer.
- Exact task in `Ready for validation`: route to `task-validator` with the exact task pointer.
- Explicit Done-task revalidation: route to `task-validator` in audit mode with original exact pointers; preserve original history and accept its distinct dated report.
- Explicit Blocked-task resume: reconcile durable owner/action, dependencies and the slot, then resume that owner.
- Explicit resume of one reconciled `Active` task: route to `task-executor` with that exact task pointer.

For other worktree-changing requests, use coarse triage:

- Route to `planner` in fast-plan mode only when the target and result are known and localized; the change stays inside one existing component or module (its existing source plus test files) and adds no production file or structure; it changes no public API, export, or cross-component interface and has no dependency, persisted or serialized data shape, security/authentication/permission, build, deployment, or runtime-configuration effect; any behaviour change is tested in the same task; and affected references and validation are certain. Cosmetic and maintenance edits qualify. The task marker remains `trivial-fast-path`.
- Route everything else to `architect` for deep triage. When uncertain, choose architect.

Never skip the planner's executable task contract or validation, even on the fast path; planner routes to architect when any fast-path condition fails. After architect triage, honor `ui_design_needed`; route through `ui-designer` when true, then return to `architect` to reconcile completed design from required to current before `planner`. Do not route to planner while the summary still marks UI design required; architect keeps missing/stale design required and returns it to its owner.

## Run exact work

Run only an exact `task_id` and `task_file` that planner returned or persisted in the canonical task stores. Pass the same pair through executor, debugger repair, and validator role transitions. Never let executor or validator discover "the active task" or "the next task."

On an explicit resume, reconcile the exact pointers and dependencies, then transition to task-executor for Active work or task-validator for Ready work. For Blocked repair, apply the durable repair-resume and dependency/slot rules in [routing-and-handoffs.md](references/routing-and-handoffs.md). For Done revalidation and untraced legacy audits, apply [requirements-and-checkpoints.md](references/requirements-and-checkpoints.md).

After PASS, dispatch the one exact dependency-ready Pending task covered by recorded batch authority or a new user continuation choice. If no unique pointer is persisted, route to planner to select within that scope; do not guess.

For each role transition, carry only the original request or a faithful clean restatement, the exact `requirement_id`, one-line artifact pointers, and the exact task pointer for task-bound work. For a linked-detail requirement, always include the detailed requirements file among those artifact pointers and direct the role to read it with the root entry as the complete requirement. Do not quote, summarize, or relay prior specialist output; make each role read the shared artifacts.

Read only the specialist skill's strict JSON handoff to route the next step. Validate its schema and artifact pointers, respect its `next` recommendation unless a stated protocol rule or explicit user redirect overrides it, and reject malformed or contradictory handoffs. Also reject a handoff or task contract that introduces implementation structure not disclosed and authorized by the confirmed REQ. Route avoidable internal expansion to planner, architecture/design expansion to its owner, and missing user authority to the orchestrator decision checkpoint; agent-authored justification does not cure the gap.

## Keep repair loops bounded

Automatically follow a valid repair handoff while it remains inside the accepted requirement and exact task. Preserve the validation-report pointer and task pointer throughout the loop.

Pause at a decision checkpoint when a repair changes accepted scope, needs a material architecture or UI choice, reaches diagnosis-only completion or any other terminal non-implementation result, or reports a terminal top-level blocker. Treat a task-level `Blocked` state with a named repair owner as an automatic route, not automatically as a user checkpoint.

## End at the right checkpoint

Record explicit batch authority and its stopping point in the existing free-form REQ. Do not infer it from a task list or Ready state alone. After delivery PASS, report the exact task, evidence and requirement state. Within that authority, the checkpoint is a progress update and the next exact eligible task continues sequentially. Without it, present the user's next-step choices. Stop at the authorized endpoint, user stop, changed scope, material decision, terminal blocker, or final acceptance. A Done audit never grants continuation.

Close a requirement only after all acceptance criteria have durable evidence and the user accepts the outcome at the applicable iteration or terminal decision checkpoint. Keep it `In Progress` when one task passes but requirement-level work remains.

## Preserve the operating boundary

- Own the additive conversational preflight for new request candidates.
- Own requirement lifecycle, linked detailed requirements files, the minimal `requirements.md` registry, coarse triage, exact task sequencing, repair routing, and checkpoints.
- Let architect own deep triage, boundary contracts, decisions, build plans, and blast radius.
- Let ui-designer own interaction and visual design contracts.
- Let planner own task design and task documents.
- Let task-executor own implementation of one exact task.
- Let debugger own defect reproduction and root-cause investigation.
- Let task-validator own the quality gate and terminal task completion.
- Let doc-cleanup own eligible SPIDER documentation cleanup and archival.

When a role crosses its boundary, reject the handoff and redirect the work to the owner.
