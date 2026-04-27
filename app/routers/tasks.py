from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Priority, TaskStatus, User
from app.schemas import (
    CommentCreate,
    CommentResponse,
    TaskAnalytics,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services import analytics_service, task_service
from app.models import Comment

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_owner(owner_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ── CRUD ───────────────────────────────────────────────


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreate,
    owner_id: int = Query(..., description="ID of the task owner"),
    db: Session = Depends(get_db),
):
    _get_owner(owner_id, db)
    return task_service.create_task(db, payload, owner_id)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    owner_id: int = Query(...),
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return task_service.list_tasks(db, owner_id, status, priority, skip, limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)
):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.update_task(db, task, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_service.delete_task(db, task)


# ── Priority escalation ───────────────────────────────


@router.post("/{task_id}/escalate", response_model=TaskResponse)
def escalate_priority(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.auto_escalate_priority(db, task)


@router.post("/{task_id}/clone", response_model=TaskResponse, status_code=201)
def clone_task(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.clone_task(db, task, task.owner_id)


@router.post("/{task_id}/defer", response_model=TaskResponse)
def defer_task(task_id: int, days: int = Query(..., ge=1), db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.defer_task_due_date(db, task, days)


@router.post("/{task_id}/reassign", response_model=TaskResponse)
def reassign_task(task_id: int, new_owner_id: int = Query(...), db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    _get_owner(new_owner_id, db)
    return task_service.reassign_task_owner(db, task, new_owner_id)


@router.post("/bulk/cancel")
def bulk_cancel_tasks(owner_id: int = Query(...), db: Session = Depends(get_db)):
    cancelled_count = task_service.bulk_cancel_open_tasks(db, owner_id)
    return {"cancelled_count": cancelled_count}


# ── Comments ───────────────────────────────────────────


@router.post("/{task_id}/comments", response_model=CommentResponse, status_code=201)
def add_comment(
    task_id: int,
    payload: CommentCreate,
    author_id: int = Query(...),
    db: Session = Depends(get_db),
):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = Comment(body=payload.body, task_id=task_id, author_id=author_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{task_id}/comments", response_model=list[CommentResponse])
def list_comments(task_id: int, db: Session = Depends(get_db)):
    task = task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.comments


# ── Analytics ──────────────────────────────────────────


@router.get("/analytics/summary", response_model=TaskAnalytics)
def task_analytics(owner_id: int = Query(...), db: Session = Depends(get_db)):
    return analytics_service.get_analytics(db, owner_id)
