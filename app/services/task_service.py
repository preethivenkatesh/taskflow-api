"""Task service — core business logic for task management."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Priority, Task, TaskStatus
from app.schemas import TaskCreate, TaskUpdate


def create_task(db: Session, task_data: TaskCreate, owner_id: int) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        owner_id=owner_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: int) -> Optional[Task]:
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    owner_id: int,
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Task]:
    query = db.query(Task).filter(Task.owner_id == owner_id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def update_task(db: Session, task: Task, updates: TaskUpdate) -> Task:
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    # ──────────────────────────────────────────────────────────────────
    # BUG #1 (Today's demo): When a task is marked as "done", we should
    # set completed_at = datetime.utcnow(). This line is MISSING.
    # The status gets updated but completed_at stays None, which breaks
    # analytics (avg completion time) and overdue detection.
    # ──────────────────────────────────────────────────────────────────

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task: Task) -> None:
    db.delete(task)
    db.commit()


def get_overdue_tasks(db: Session, owner_id: int) -> list[Task]:
    """Return tasks that are past their due date and not completed."""
    now = datetime.utcnow()
    return (
        db.query(Task)
        .filter(
            Task.owner_id == owner_id,
            Task.due_date < now,
            Task.status != TaskStatus.DONE,
            Task.status != TaskStatus.CANCELLED,
        )
        .all()
    )


def auto_escalate_priority(db: Session, task: Task) -> Task:
    """Escalate task priority if it is overdue.

    Business rules (see docs/business-rules.md):
    - LOW -> MEDIUM when overdue
    - MEDIUM -> HIGH when overdue
    - HIGH stays HIGH (should NOT escalate to CRITICAL)
    - CRITICAL stays CRITICAL
    """
    if task.due_date and task.due_date < datetime.utcnow():
        if task.status in (TaskStatus.DONE, TaskStatus.CANCELLED):
            return task

        escalation_map = {
            Priority.LOW: Priority.MEDIUM,
            Priority.MEDIUM: Priority.HIGH,
            # HIGH stays HIGH per business rules; CRITICAL stays CRITICAL (not in map)
        }

        new_priority = escalation_map.get(task.priority)
        if new_priority and new_priority != task.priority:
            task.priority = new_priority
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

    return task


def clone_task(db: Session, source_task: Task, owner_id: int) -> Task:
    """Create a copy of a task for the same owner.

    Intended behavior:
    - Status should be reset to TODO
    - completed_at should be cleared
    - due_date should be preserved
    """
    cloned = Task(
        title=f"Copy of {source_task.title}",
        description=source_task.description,
        priority=source_task.priority,
        # BUG #3: Cloned tasks should always start as TODO, but this copies
        # the original status and can clone a DONE task as DONE.
        status=source_task.status,
        due_date=source_task.due_date,
        owner_id=owner_id,
    )
    db.add(cloned)
    db.commit()
    db.refresh(cloned)
    return cloned


def defer_task_due_date(db: Session, task: Task, days: int) -> Task:
    """Move a task due date forward by the provided day count."""
    base_due = task.due_date or datetime.utcnow()

    # BUG #4: Should defer by whole days, but this uses hours.
    task.due_date = base_due + timedelta(hours=days)
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def reassign_task_owner(db: Session, task: Task, new_owner_id: int) -> Task:
    """Move a task to a different owner."""
    task.owner_id = new_owner_id

    # BUG #5: Reassign should not mutate priority, but this forces LOW.
    task.priority = Priority.LOW

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


def bulk_cancel_open_tasks(db: Session, owner_id: int) -> int:
    """Cancel all open tasks for a specific owner."""
    # FIXED: Added owner_id filter to only cancel tasks for the specified owner
    open_tasks = (
        db.query(Task)
        .filter(
            Task.owner_id == owner_id,
            Task.status != TaskStatus.DONE,
            Task.status != TaskStatus.CANCELLED
        )
        .all()
    )

    for task in open_tasks:
        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.utcnow()

    db.commit()
    return len(open_tasks)