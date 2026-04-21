"""Analytics service — computes task metrics for a user."""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Task, TaskStatus
from app.schemas import TaskAnalytics


def get_analytics(db: Session, owner_id: int) -> TaskAnalytics:
    tasks = db.query(Task).filter(Task.owner_id == owner_id).all()

    total = len(tasks)
    completed = [t for t in tasks if t.status == TaskStatus.DONE]
    overdue = [
        t
        for t in tasks
        if t.due_date
        and t.due_date < datetime.utcnow()
        and t.status not in (TaskStatus.DONE, TaskStatus.CANCELLED)
    ]

    # Average completion time depends on completed_at being set.
    # Because of Bug #1, completed_at is always None, so this returns None.
    completion_hours = _avg_completion_hours(completed)

    by_priority: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for t in tasks:
        by_priority[t.priority.value] = by_priority.get(t.priority.value, 0) + 1
        by_status[t.status.value] = by_status.get(t.status.value, 0) + 1

    return TaskAnalytics(
        total_tasks=total,
        completed_tasks=len(completed),
        overdue_tasks=len(overdue),
        avg_completion_hours=completion_hours,
        tasks_by_priority=by_priority,
        tasks_by_status=by_status,
    )


def _avg_completion_hours(completed_tasks: list[Task]) -> Optional[float]:
    durations = []
    for t in completed_tasks:
        if t.completed_at and t.created_at:
            delta = t.completed_at - t.created_at
            durations.append(delta.total_seconds() / 3600)
    if not durations:
        return None
    return round(sum(durations) / len(durations), 2)
