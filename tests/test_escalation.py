"""Tests for priority escalation logic.

NOTE: test_high_priority_should_not_escalate_to_critical is EXPECTED TO FAIL
due to Bug #2 — see docs/business-rules.md for the correct behavior.
"""

from datetime import datetime, timedelta

from app.models import Priority, Task, TaskStatus
from app.services.task_service import auto_escalate_priority


def _make_task(db, owner_id, priority=Priority.MEDIUM, due_date=None, status=TaskStatus.TODO):
    task = Task(
        title="Test task",
        priority=priority,
        due_date=due_date,
        status=status,
        owner_id=owner_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def test_low_escalates_to_medium_when_overdue(db, client, sample_user):
    yesterday = datetime.utcnow() - timedelta(days=1)
    task = _make_task(db, sample_user["id"], Priority.LOW, yesterday)
    result = auto_escalate_priority(db, task)
    assert result.priority == Priority.MEDIUM


def test_medium_escalates_to_high_when_overdue(db, client, sample_user):
    yesterday = datetime.utcnow() - timedelta(days=1)
    task = _make_task(db, sample_user["id"], Priority.MEDIUM, yesterday)
    result = auto_escalate_priority(db, task)
    assert result.priority == Priority.HIGH


def test_high_priority_should_not_escalate_to_critical(db, client, sample_user):
    """HIGH priority tasks must NOT escalate to CRITICAL per business rules.
    This test FAILS due to Bug #2 — the escalation map incorrectly
    maps HIGH -> CRITICAL. See docs/business-rules.md."""
    yesterday = datetime.utcnow() - timedelta(days=1)
    task = _make_task(db, sample_user["id"], Priority.HIGH, yesterday)
    result = auto_escalate_priority(db, task)
    # Bug #2: this will fail because HIGH incorrectly escalates to CRITICAL
    assert result.priority == Priority.HIGH, (
        "HIGH priority tasks should NOT be auto-escalated to CRITICAL "
        "(see docs/business-rules.md)"
    )


def test_completed_task_not_escalated(db, client, sample_user):
    yesterday = datetime.utcnow() - timedelta(days=1)
    task = _make_task(
        db, sample_user["id"], Priority.LOW, yesterday, TaskStatus.DONE
    )
    result = auto_escalate_priority(db, task)
    assert result.priority == Priority.LOW


def test_task_not_overdue_not_escalated(db, client, sample_user):
    tomorrow = datetime.utcnow() + timedelta(days=1)
    task = _make_task(db, sample_user["id"], Priority.LOW, tomorrow)
    result = auto_escalate_priority(db, task)
    assert result.priority == Priority.LOW
