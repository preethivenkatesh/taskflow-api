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
