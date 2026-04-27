# TaskFlow API Business Rules

## Priority Levels

Tasks have four priority levels: `low`, `medium`, `high`, `critical`.

### Manual assignment
- Users can set any priority when creating or updating a task.
- `CRITICAL` priority can **only be set manually** by a user — it must never
  be assigned by automated processes.

## Automatic Priority Escalation

When a task becomes overdue (current time > due_date) and has not been
completed or cancelled, the system may automatically escalate its priority.

### Escalation rules

| Current Priority | Escalated To | Notes |
|-----------------|-------------|-------|
| `low`           | `medium`    | Standard escalation |
| `medium`        | `high`      | Standard escalation |
| `high`          | `high`      | **No change** — HIGH is the maximum auto-escalation level |
| `critical`      | `critical`  | No change — already at highest level |

> **Important**: `CRITICAL` is reserved for human-assigned emergencies.
> The auto-escalation system must NEVER promote a task to `critical`.
> This prevents alert fatigue and preserves the signal value of critical tasks.

## Task Completion

When a task's status is changed to `done`:
1. The `completed_at` timestamp MUST be set to the current UTC time.
2. The task should no longer appear in overdue queries.
3. Analytics (avg completion time) depend on `completed_at` being accurate.

## Overdue Detection

A task is overdue when:
- `due_date` is in the past, AND
- `status` is not `done` or `cancelled`

## Comments

- Any authenticated user can comment on any task.
- Comments are append-only (no editing or deletion).

## Task Cloning

When a task is cloned:
- The cloned task title should be prefixed with `Copy of `.
- The cloned task should preserve description, priority, and due_date.
- The cloned task status MUST reset to `todo` regardless of source task status.
- The cloned task MUST have `completed_at = null`.

## Task Deferral

When a task is deferred by N days:
- If a due date exists, new due date = old due date + N days.
- If no due date exists, new due date = current UTC time + N days.
- `days` must be a positive integer.

## Task Reassignment

When a task is reassigned to another owner:
- `owner_id` must be updated to the target user.
- Task content should be preserved.
- Priority MUST remain unchanged.

## Bulk Cancel

When bulk-cancel is requested for an owner:
- Only tasks belonging to that owner are eligible.
- Only open tasks (`todo`, `in_progress`) should transition to `cancelled`.
- `done` and already `cancelled` tasks must be unchanged.
