# SPIDER Agent Flows

## Entry and requirement state

Every repository-changing request starts with the orchestrator and one stable requirement. Read-only questions, status checks, and commit-only operations may be handled directly.

```text
User request (new change)
  -> orchestrator preflight: discover, resolve ambiguity, confirm the final proposal
  -> confirmed: create REQ as Ready -> In Progress on first dispatch
Continuation or repair inside an accepted REQ
  -> reuse that REQ
```

Material ambiguity in a new request is resolved in preflight before any REQ exists; a new request is never recorded as Draft.

The orchestrator alone updates requirement state:

`Ready -> In Progress -> Done`, with `In Progress -> Draft -> Ready` only when unresolved user intent is discovered.

`Draft`, `Ready`, or `In Progress` may become `Superseded`. Supersession cancels every linked non-terminal task; an Active or Ready-for-validation task is stopped and reconciled first. `In Progress -> Draft` is allowed only when unresolved user intent is discovered. Technical blockers stay in task or defect state. `Done` normally requires complete validator evidence plus the user's iteration checkpoint. Diagnosis-only and cleanup-only REQs use their named specialist's durable terminal evidence when no implementation validation applies.

Every new lifecycle or history event records the actual current time as a second-precision ISO 8601 timestamp (`YYYY-MM-DDTHH:mm:ss±HH:mm` or `Z`). Requirement capture/amendments, decisions, task `Updated` values and LOG entries, DEBUG LOG/defect reports, cleanup evidence, and validation reports all follow this rule. New validator JSON uses `timestamp`; historical date-only records and legacy report `date` keys remain valid and are not backfilled.

## Minimum-change authorization loop

Every worktree-changing request uses the existing requirement and handoff chain to authorize implementation shape:

```text
request candidate
  -> orchestrator identifies the direct baseline
  -> disclose every proposed structural addition and why baseline is insufficient
  -> user confirms baseline plus any explicitly approved additions
  -> linked REQ preserves that authorization
  -> architect / UI designer / planner enforce it at their contract seam
  -> executor / debugger / doc-cleanup stay inside it
  -> validator compares contract + manifest + diff and fails a mismatch
```

When a direct implementation satisfies the REQ, specialist justification, consistency, future reuse, taxonomy, or hypothetical scale cannot authorize more structure. A newly discovered need routes to the existing planner or architect/UI owner and then to orchestrator when user authority is missing.

## Main delivery flow

```text
                          Orchestrator
                               |
                   +-----------+-----------+
                   |                       |
          fast change                 everything else
                   |                       |
          Planner fast-plan            Architect
          (REQ-linked task)        impact + plan freshness
                   |                 + independent UI need
                   |                       |
                   |              ui_design_needed?
                   |                 /           \
                   |               yes            no
                   |                |              |
                   |          UI designer          |
                   |                |              |
                   |     Architect readiness       |
                   |                |              |
                   +----------------+--------------+
                                    |
                                 Planner
                                    |
                         exact task_id + task_file
                                    |
                                 Executor
                   Pending -> Active -> Ready for validation
                                    |
                                 Validator
                           /                    \
                        PASS                    FAIL
                         |                       |
                       Done              exact repair owner
                         |                       |
                iteration checkpoint      repaired same task
                                                  |
                                              Validator
```

A fast change skips architect, never planner or validator. It qualifies only when the target and result are known and localized; it stays inside one existing component or module (source plus test files) and adds no production file or structure; it changes no public API, export, or cross-component interface and has no dependency, persisted or serialized data shape, security/authentication/permission, build, deployment, or runtime-configuration effect; and any behaviour change is tested in the same task. Doubt routes to architect. Planner routes it to architect if repository inspection invalidates any fast-path condition, and validator fails a misclassified fast task.

## Architect outputs

Architect returns three independent fields:

- `triage`: `no-impact | needs-architecture`
- `plan_freshness`: `not-required | current | refreshed | missing | stale`
- `ui_design_needed`: `true | false`

These values are persisted in `features/<slug>/blast-radius-summary.md` as `Architecture triage`, `Plan freshness`, and `UI design`. The UI field is one of `required: <design path>`, `current: <design path>`, or `not-required`.

After a completed or amended design, the route is:

`ui-designer -> architect readiness reconciliation -> planner`

Planner is the peer owner of code-level implementation design. It converts these upstream contracts into the minimum sufficient implementation and the fewest cohesive tasks; architecture components and UI anatomy are not automatic code artifacts or task boundaries.

When planner has repository and requirement evidence that an architect-mandated boundary violates KISS or lacks confirmed user authorization, the closed peer challenge is:

`planner (exact boundary + evidence + direct alternative) -> architect (durably simplify, or point to confirmed REQ authorization) -> planner`

## Task state and exact pointers

Task state is:

`Pending -> Active -> Ready for validation -> Done`

An executable task may become `Blocked`. Validator FAIL returns the exact task to `Active` only when existing typed STEPS already authorize the repair; otherwise it remains `Blocked` for its contract owner. `Cancelled` is a terminal task state used when the owning REQ is Superseded; validator does not validate it. Only validator may set `Done`.

At most one task may be Active or Ready for validation. Every task-bound handoff preserves the exact `requirement_id`, `task_id`, and `task_file`; no agent discovers an arbitrary active or next task.

## Closed repair loops

Already-authorized repair loops continue automatically inside the current iteration:

| Trigger | Route back to validation |
|---|---|
| Existing STEP was skipped or implemented mechanically wrong | validator -> executor -> validator |
| Task trace, GOAL, internal structure, wiring, test strategy, or STEPS gap | validator/executor -> planner -> executor -> validator |
| Hypothesis-driven defect under an exact current task | validator/executor synchronizes the task to `Blocked` -> debugger -> executor or validator according to remaining STEPS |
| Decision, component boundary, public API, dependency, plan, blast-radius gap, or planner KISS challenge | validator/planner/debugger -> architect (durably simplify or justify) -> optional [UI -> architect readiness reconciliation] -> planner -> executor -> validator |
| Missing, stale, or contradictory UI interaction contract | validator/architect -> UI designer -> architect readiness reconciliation -> planner -> executor -> validator |
| Missing, Draft, contradictory, or expanded user-visible requirement | any agent -> orchestrator -> user decision when material -> normal triage |
| Undisclosed or unapproved implementation structure | any agent -> planner or architect/UI owner -> orchestrator when user authority is missing -> normal task/validation loop |

## Taskless defect flow

```text
User-reported bug with no authorized task
  -> orchestrator creates Ready defect REQ and dispatches taskless debugger
  -> debugger diagnoses only and writes features/<slug>/defects/bug-req-N-<slug>.md
       -> diagnosis-only request: user decision checkpoint
       -> remediation requested: architect impact/plan/UI triage
            -> optional [UI designer -> architect readiness reconciliation]
            -> planner remediation task
            -> executor
            -> validator
```

A taskless REQ or defect report never authorizes source edits. For a task-linked defect, debugger may apply a localized fix only inside the accepted requirement and upstream boundaries.

## Path summary

| Path | Trigger | Agents |
|---|---|---|
| Direct | Read-only/status/commit-only request | orchestrator |
| Fast plan | Known localized change inside one existing component, no new structure or public/system effect, behaviour tested in the task | orchestrator -> planner -> executor -> validator -> user |
| Isolated change | No architecture change, no current build plan needed | orchestrator -> architect (`no-impact + not-required`) -> optional [UI -> architect readiness reconciliation] -> planner -> executor -> validator -> user |
| Current plan | Existing plan and blast summary cover the REQ | orchestrator -> architect (`no-impact + current`) -> optional [UI -> architect readiness reconciliation] -> planner -> executor -> validator -> user |
| New/changed architecture | Boundary, public API, dependency, persisted shape, or cross-cutting constraint changes | orchestrator -> architect (`needs-architecture + refreshed`) -> optional [UI -> architect readiness reconciliation] -> planner -> executor -> validator -> user |
| Task-linked defect | Exact current task is Blocked with a hypothesis-driven failure | executor/validator -> debugger -> executor or validator, or escalation through contract owner |
| Taskless defect | User bug has no authorized current task, including a regression against Done/history | orchestrator -> debugger report -> architect -> optional [UI -> architect readiness reconciliation] -> planner -> executor -> validator -> user |
| Done revalidation | Explicit audit of exact Done task | validator -> distinct report -> user (PASS) or orchestrator/requested new linked work (FAIL); original history unchanged |
| Cleanup | Explicit REQ-linked documentation compaction request | orchestrator -> doc-cleanup -> durable cleanup evidence -> user |
