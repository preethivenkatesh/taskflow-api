"""Task service — core business logic for task management."""

from datetime import datetime
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

        # ──────────────────────────────────────────────────────────────
        # BUG #2 (Future RAG demo): HIGH escalates to CRITICAL here,
        # but business-rules.md says HIGH should stay HIGH.
        # An agentic AI would need to retrieve docs/business-rules.md
        # to understand this is wrong.
        # ──────────────────────────────────────────────────────────────
        escalation_map = {
            Priority.LOW: Priority.MEDIUM,
            Priority.MEDIUM: Priority.HIGH,
            Priority.HIGH: Priority.CRITICAL,  # BUG: should stay HIGH
        }

        new_priority = escalation_map.get(task.priority)
        if new_priority and new_priority != task.priority:
            task.priority = new_priority
            task.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(task)

    return task
