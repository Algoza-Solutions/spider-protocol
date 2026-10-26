# Routing and handoffs

## Contents

- Canonical artifacts and task state
- Routing matrix
- Role-transition payload
- Handoff validation
- Repair routes
- Role enforcement

## Canonical artifacts and task state

Treat these human-readable artifacts as Markdown: `project.md`, `requirements.md`, `decisions.md`, `architecture/architecture.md`, `features/<slug>/build-plan.md`, `features/<slug>/blast-radius-summary.md`, and `features/<slug>/tasks/*.md`.

When an exact `requirements.md#REQ-N` entry contains an inline link to a detailed requirements file, treat that linked Markdown file as the detailed body of the same canonical REQ. Resolve and read the entry and linked body together. The detailed file has no prescribed path or internal layout.

Treat `features/<slug>/design.html` as the sole human-readable HTML exception and `task-index.yaml` as machine-readable state. If equivalent non-design `.md` and `.html` artifacts coexist, prefer Markdown and treat HTML as a stale migration candidate unless a later decision says otherwise.

Reconcile the exact task across `task-index.yaml`, `project.md`, and its canonical task document. Permit only one task in the delivery slot: `Active` or `Ready for validation`. `Done` and `Cancelled` are terminal. A Cancelled task never satisfies a dependency unless planner repairs the dependency.

Allow historical Blocked tasks to coexist, but reserve the current iteration for a named repair loop. Do not run unrelated Pending work until that repair reaches validation or a terminal checkpoint.

## Routing matrix

| Situation | Route |
|---|---|
| SPIDER question, read-only status, explicit commit management | Orchestrator handles directly |
| Documentation cleanup or archival | Ready REQ -> doc-cleanup |
| User bug without an authorized task | Ready REQ -> taskless debugger diagnosis |
| Remediation after taskless diagnosis | debugger report -> architect -> optional [ui-designer -> architect readiness reconciliation] -> planner |
| Defect on exact current Blocked task | debugger with exact task pointer after dependency/slot guards |
| Explicit resume of exact Blocked repair | reconcile latest durable owner/action; resume that owner after guards |
| Explicit Done-task revalidation | task-validator audit with original exact pointers and distinct report |
| Exact task Ready for validation | task-validator with exact task pointer |
| Explicit resume of one exact Active task | task-executor with exact task pointer |
| Recorded batch authority or user continue covers one exact eligible persisted Pending task | task-executor with exact task pointer |
| Continuation is authorized but the next pointer is missing or ambiguous | planner selects or repairs sequence, then returns one exact task pointer |
| Known localized change inside one existing component (source plus tests), adding no production file or structure and no public API, export, cross-component, dependency, data-shape, security, build, deployment, or runtime-configuration effect; behaviour changes tested in the task | Ready REQ -> planner fast-plan |
| Any other change | Ready REQ -> architect deep triage |

From architect, treat `triage`, `plan_freshness`, and `ui_design_needed` as independent routing fields. Reject a `DONE` handoff whose required plan or blast-radius artifact is missing or stale. Route through ui-designer whenever `ui_design_needed` is true, even when architectural impact is `no-impact`.

After any completed or amended design, route ui-designer back to architect
with the same requirement and any exact task pointer. Architect verifies the
design's REQ, path, content, applicable build-plan link, and scope before
changing the summary's UI disposition from required to current. Its handoff
must match the reconciled metadata with ui_design_needed false before planner.
Missing/stale design remains required and routes back to the proper owner.
Reject a planner transition while UI metadata is still required.

Planner must return the one exact `task_id` and `task_file` to run. Transition to task-executor for that task, then transition to task-validator for the same task.

Before transitioning to task-executor, require the task to reference a current blast-radius summary or carry a valid typed trivial-fast-path scope. If neither exists, route the exact task to planner for contract repair; do not let executor start it.

## Durable repair resume

For an exact nonterminal repair, reconcile NOW/LOG and the latest applicable
report. A newer accepted route supersedes the original failure owner. Persist
accepted owner/action/reason in NOW.Next and an ISO-8601-stamped LOG entry without
changing task lifecycle, checkboxes, or implementation. Missing owner
evidence falls back to planner; conflicting evidence returns to planner or the
identified contract owner for reconciliation, never a guessed route.

Before task-linked mutation or Active/Ready promotion, verify dependencies
and that no other task occupies the delivery slot. Waiting work remains
Blocked with a durable owner/action/reason and returns to orchestrator without
displacing work or busy-looping. Resume when the obstacle clears. A reserved
repair precedes unrelated Pending work unless the user redirected the iteration.

A waiting handoff uses next: orchestrator while preserving the actual repair
owner/action. This takes precedence over direct failure-owner routing. Planner
may correct only invalid dependency/routing metadata while Blocked; implementation,
shared-artifact edits and promotion remain guarded.

Done revalidation and untraced legacy audits follow the single statement in
[requirements-and-checkpoints.md](requirements-and-checkpoints.md).

## Role-transition payload

Pass only:

1. The original user request verbatim or as a faithful clean restatement.
2. The exact `requirement_id` and pointer to `requirements.md`.
3. One-line pointers to relevant canonical artifacts.
4. The exact `task_id` and `task_file` for every task-bound specialist invocation, including repair planning, architecture, UI, executor, debugger, and validator work.

Do not shuttle prior specialist summaries or quoted outputs. Load each named skill sequentially in the current thread and make it read shared artifacts. Preserve the strict JSON handoff data defined by its skill contract for routing, but do not launch a subagent to obtain it.

For a linked-detail REQ, the one-line artifact pointers must include the exact detailed requirements path and direct the role to read it with `requirements.md#REQ-N` as one requirement contract.

Never use subagent, delegation, or collaboration tools to run a SPIDER role. A route means a current-thread skill transition, not a new agent process.

## Handoff validation

Accept a handoff only when it is a single valid JSON object without Markdown fences, comments, or trailing commas. Require all fields defined by the specialist skill contract.

For every handoff:

- Verify `requirement_id` matches the routed requirement.
- When the requirement entry links a detailed file, verify that the link resolves and the role-transition payload points to that same path.
- Verify artifact paths exist when the handoff claims they were created or updated. Done-revalidation handoffs list the new report, with no task/state-store writes; requirement_ready_to_close is false.
- Verify `next` names a valid owner or checkpoint.
- For task-bound work, require `task_id` and `task_file`; verify the same task in index/project/task. In an explicitly identified untraced legacy audit, requirement_id names the audit-request REQ while original task/index trace stays absent; reject a contradictory existing trace.
- Preserve the same task pointer across executor, debugger repair, and validator.
- Preserve `features/<slug>/validation/tN-validation.json` through delivery repair loops once it exists. Done audits instead point to a distinct `tN-revalidation-YYYYMMDDTHHmmss[-suffix].json` report and never replace original evidence.
- Respect `next` unless an explicit user redirect or recorded batch authority overrides a delivery PASS checkpoint; state the reason. Audit PASS/FAIL does not authorize continuation or old-task repairs.
- Reject contradictory, missing, or malformed fields and return the handoff to its author for repair.
- Compare proposed implementation shape with the confirmed linked REQ. Reject undisclosed or unapproved added structure even when a specialist provides its own justification. Route avoidable internal expansion to planner, architecture/design expansion to its owner, and missing user authority to orchestrator for the existing decision checkpoint.

## Repair routes

Follow these routes automatically while they remain inside the accepted requirement and exact task:

- Implementation defect -> executor, or validator-authorized debugger -> validator
- Task or STEPS gap -> planner -> executor -> validator
- Architecture, plan, or blast-radius gap -> architect -> optional [ui-designer -> architect readiness reconciliation] -> planner -> executor -> validator
- UI-contract gap -> ui-designer -> architect readiness reconciliation -> planner -> executor -> validator

Pause for a user decision when a repair changes accepted scope, needs a material choice, reports a terminal top-level blocker, or terminates as diagnosis-only or other non-implementation work.

Done-audit FAIL returns to orchestrator. Requested new defect work uses a new linked REQ and taskless diagnosis; audit-only work may end with its findings. Preserve original task state and reports.

## Role enforcement

| Boundary violation | Redirect to |
|---|---|
| Planner writes code | task-executor |
| Executor creates or rescopes tasks | planner |
| Executor makes architecture decisions | architect |
| Validator modifies implementation | task-executor or debugger as authorized |
| Planner designs screens, flows, or interactions | ui-designer |
| UI designer defines backend architecture or APIs | architect |
| UI designer creates implementation tasks | planner |
| Planner or executor cleans historical docs | doc-cleanup |
| Executor performs open-ended investigation | debugger |
| Debugger creates tasks | planner |
| Debugger changes architecture | architect |
| Planner plans work outside the fast path without a current blast-radius summary | architect, then planner |
| Executor transition lacks both a current blast-radius reference and a typed fast-path scope | planner |
| Any role introduces structure not disclosed and authorized by the confirmed REQ | planner or the owning architect/ui-designer, then orchestrator when user authority is missing |

Tasks follow the planner's KISS scoping: the fewest cohesive, independently implementable and verifiable tasks. One task may span several files, layers, or components when they form one outcome; do not demand a split merely because work mentions a component, service, helper, page, or module. Route a task that bundles unrelated outcomes, or a fragment that leaves a required path half-built, back to planner for rescoping.
