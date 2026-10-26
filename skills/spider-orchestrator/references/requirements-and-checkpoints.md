# Requirements and checkpoints

## Requirement record

For a new preflight-confirmed request, write the complete requirement to a separate Markdown file and add only a stable linked registry entry to `requirements.md`. Do not overwrite earlier entries. Insert the new REQ before older REQs, immediately after the document's fixed title and preamble.

Do not prescribe a template, fixed headings, fixed section order, or standard layout for the detailed requirements file. Organize it to make the confirmed requirement clear. Keep stable `AC-N` identifiers somewhere in its content because existing task and validation traceability depends on them.

```markdown
## REQ-[N]: [Short title]

**Timestamp:** YYYY-MM-DDTHH:mm:ss?HH:mm
**Status:** Draft | Ready | In Progress | Done | Superseded
**User request:** [Concise confirmed request]
**Detailed requirements:** [Descriptive document title](relative/path/to/detailed-requirements.md)
**Superseded by:** REQ-N | N/A

### Acceptance criteria (user-facing)
- [ ] **AC-1:** [Concise user-facing criterion; full definition in the linked detailed requirements.]

### Validation evidence
- **AC-1:** Pending
```

Create one concise root acceptance summary and one evidence placeholder for every `AC-N` defined in the detailed file. Keep full descriptive requirement content in the linked file instead of duplicating it in `requirements.md`. The root summaries preserve the existing `REQ-N`/`AC-N` task and validator trace, while the inline-linked file is the detailed body of that same exact requirement, not supplemental context. Reading the REQ "in full" means reading the registry entry and linked body together. Before routing, verify that the link resolves to the file just written. Do not migrate or rewrite historical full entries.

The free-form detailed requirement also preserves the confirmed
implementation-shape authorization. Record the direct baseline—the smallest
change using existing code, structures, conventions, and owners—and every
additional structure the user explicitly approved after disclosure. When no
addition is approved, make the minimum-direct-change posture unambiguous. Do
not add a mandatory heading, registry field, approval ledger, or score.

## Continuation authority

Record the user's explicit batch scope and stopping point in the existing
free-form requirement, using ordinary prose. It may cover named tasks or the
requirement's planned implementation. A task list, Ready state, or approval of
one task alone is not broader authority. Preserve user stops and later scope
changes; no new field, ledger, or scheduler is needed.

## Lifecycle

1. Reuse the requirement already referenced by an in-scope continuation or repair. Do not duplicate it.
2. Set a preflight-confirmed request to `Ready` without an extra approval round. Resolve material ambiguity in a new request during preflight; never record a new request as `Draft`.
3. Return an `In Progress` requirement to `Draft` only when a specialist surfaces unresolved user intent; ask the smallest necessary question and do not route it until it is `Ready` again.
4. Set a Ready requirement to `In Progress` when transitioning to its first specialist skill or exact implementation task.
5. Set it to `Done` only after every acceptance criterion has durable evidence and the user accepts closure at the applicable iteration checkpoint or terminal decision checkpoint.
6. Use the terminal specialist report as evidence for accepted diagnosis-only, no-op, or cleanup-only work. Do not imply that remediation shipped.
7. Include `requirement_id: "REQ-N"` and a pointer to `requirements.md` in every downstream handoff.

Keep acceptance criteria in the detailed file user-facing and testable. Record constraints the user actually stated; do not invent scope. A request that exists only in chat is not a routable requirement. Include the detailed file path as a one-line relevant-artifact pointer in every downstream handoff for that requirement and explicitly direct the role to read both files as the exact REQ contract.

## Amendments and history

- Add a timestamped amendment for post-Ready clarification. Insert it before older amendments in that REQ's amendment history while preserving the original request and accepted criteria.
- Give a material follow-up after Done a new linked requirement.
- Treat a regression against a Done task or requirement as new work and use the taskless bug path. Explicit Done revalidation preserves the original task/REQ/state/report and writes distinct dated audit evidence; requested follow-up gets a new linked REQ.
- Before superseding an In Progress requirement, stop and reconcile its Active or Ready-for-validation task. Route Pending or Blocked tasks to planner for consistent `Cancelled` state across all stores.
- Keep Done history immutable. State the replacement and reason on a Superseded entry.

Use the actual current time as a timezone-qualified ISO 8601 timestamp for every new requirement record, amendment, lifecycle note, and checkpoint-evidence entry: `YYYY-MM-DDTHH:mm:ss?HH:mm` (or `Z`). Do not emit date-only output. Historical date-only records remain valid; add a new timestamped event instead of inventing a time for old history.

## Decision checkpoint

Pause and request user direction when:

- An `In Progress` requirement returned to `Draft` needs material clarification.
- An architecture or UI choice changes accepted behavior or scope.
- A specialist reports a terminal top-level `BLOCKED` result.
- A diagnosis-only investigation reaches its terminal report.
- Any other specialist reaches a terminal non-implementation or no-op result.
- Multiple tasks occupy the delivery slot or canonical task stores contradict each other.

Report the decision, essential context, available options, and a recommendation. Do not proceed until the user decides.

When the user accepts a diagnosis-only or other terminal non-implementation outcome as satisfying the requirement, record the terminal report against each applicable acceptance criterion, check those criteria, and set the requirement to `Done`. When remediation is requested or criteria remain unsatisfied, keep it `In Progress` and follow the routed remediation path.

## Done revalidation and legacy audits

Route an explicit audit of an exact Done task to task-validator in audit mode
with the original pointers. It writes a distinct dated report and leaves the
original task, REQ, state stores, LOG, and report untouched. PASS is an audit
result; FAIL is a finding, not authority to reopen or repair old work.
Requested follow-up uses a new linked REQ and taskless diagnosis; audit-only
work may end with the report. Revalidation never grants requirement closure or
batch continuation.

For a legacy Done task whose original REQ trace is absent, orchestrator
captures a normal audit-request REQ for that exact historical task and scope.
The existing requirement_id identifies that audit request in invocation,
report and handoff; task_id/task_file remain the original legacy pointers.
Record absent origin trace in report notes without changing task/index metadata.
A contradictory existing trace is not absent and cannot use this exception.
After user acceptance, orchestrator may close the audit-only REQ from terminal
report evidence even though the audit readiness flag is always false.

## Iteration checkpoint

After delivery validator PASS, report the exact task, evidence and requirement state. Within recorded batch authority this is a progress update and the next exact dependency-ready task may proceed. Otherwise present:

```text
T[N] [Task name] - PASS. [Concise evidence summary]
Requirement: REQ-[N] - [In Progress | ready to close]

What next?
1. Continue to the next exact task
2. Run doc-cleanup
3. Do something else
4. Stop
```

Run another task after PASS only when recorded continuation authority covers it or the user chooses it. Stop at the authorized endpoint, user stop, material decision, scope change, terminal blocker, or final acceptance. When `requirement_ready_to_close` is true, show the accumulated acceptance evidence; batch execution permission alone does not accept closure. If the user accepts closure, replace each `Pending` evidence value with concise task/report references, check the satisfied criteria, and set the requirement to `Done`.

For a cleanup-only requirement, use the doc-cleanup report plus its tombstone or evidence references in place of validator evidence and present the same iteration checkpoint.
