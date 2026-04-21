"""Tests for task CRUD, completion, and analytics.

NOTE: test_complete_task_sets_completed_at and test_analytics_avg_completion_time
are EXPECTED TO FAIL due to Bug #1 — update_task does not set completed_at.
"""

from datetime import datetime, timedelta


def _create_task(client, owner_id, **overrides):
    payload = {
        "title": "Fix login page",
        "description": "Users can't log in on mobile",
        "priority": "high",
    }
    payload.update(overrides)
    resp = client.post(f"/api/v1/tasks/?owner_id={owner_id}", json=payload)
    assert resp.status_code == 201
    return resp.json()


# ── CRUD ────────────────────────────────────────────────────


def test_create_task(client, sample_user):
    task = _create_task(client, sample_user["id"])
    assert task["title"] == "Fix login page"
    assert task["status"] == "todo"
    assert task["priority"] == "high"


def test_list_tasks(client, sample_user):
    uid = sample_user["id"]
    _create_task(client, uid, title="Task A")
    _create_task(client, uid, title="Task B")
    resp = client.get(f"/api/v1/tasks/?owner_id={uid}")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_tasks_filter_by_status(client, sample_user):
    uid = sample_user["id"]
    _create_task(client, uid, title="Active task")
    resp = client.get(f"/api/v1/tasks/?owner_id={uid}&status=todo")
    assert resp.status_code == 200
    assert all(t["status"] == "todo" for t in resp.json())


def test_get_task(client, sample_user):
    task = _create_task(client, sample_user["id"])
    resp = client.get(f"/api/v1/tasks/{task['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == task["id"]


def test_update_task_title(client, sample_user):
    task = _create_task(client, sample_user["id"])
    resp = client.patch(
        f"/api/v1/tasks/{task['id']}", json={"title": "Updated title"}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated title"


def test_delete_task(client, sample_user):
    task = _create_task(client, sample_user["id"])
    resp = client.delete(f"/api/v1/tasks/{task['id']}")
    assert resp.status_code == 204
    resp = client.get(f"/api/v1/tasks/{task['id']}")
    assert resp.status_code == 404


# ── Completion bug ──────────────────────────────────────────


def test_complete_task_sets_completed_at(client, sample_user):
    """Completing a task MUST set completed_at. This test FAILS due to Bug #1."""
    task = _create_task(client, sample_user["id"])
    resp = client.patch(
        f"/api/v1/tasks/{task['id']}", json={"status": "done"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    # This assertion will FAIL — completed_at is None because update_task
    # doesn't set it when status transitions to "done".
    assert data["completed_at"] is not None, (
        "completed_at should be set when task is marked done"
    )


# ── Analytics ───────────────────────────────────────────────


def test_analytics_counts(client, sample_user):
    uid = sample_user["id"]
    _create_task(client, uid, title="T1")
    _create_task(client, uid, title="T2")
    resp = client.get(f"/api/v1/tasks/analytics/summary?owner_id={uid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] == 2
    assert data["completed_tasks"] == 0


def test_analytics_avg_completion_time(client, sample_user):
    """avg_completion_hours should return a number after completing tasks.
    This test FAILS due to Bug #1 — completed_at is never set."""
    uid = sample_user["id"]
    task = _create_task(client, uid)

    # Complete the task
    client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "done"})

    resp = client.get(f"/api/v1/tasks/analytics/summary?owner_id={uid}")
    data = resp.json()
    assert data["completed_tasks"] == 1
    # This will FAIL — avg_completion_hours is None because completed_at is None
    assert data["avg_completion_hours"] is not None, (
        "avg_completion_hours should be calculated for completed tasks"
    )


# ── Comments ────────────────────────────────────────────────


def test_add_comment(client, sample_user):
    task = _create_task(client, sample_user["id"])
    resp = client.post(
        f"/api/v1/tasks/{task['id']}/comments?author_id={sample_user['id']}",
        json={"body": "Looking into this now"},
    )
    assert resp.status_code == 201
    assert resp.json()["body"] == "Looking into this now"


def test_list_comments(client, sample_user):
    task = _create_task(client, sample_user["id"])
    uid = sample_user["id"]
    client.post(
        f"/api/v1/tasks/{task['id']}/comments?author_id={uid}",
        json={"body": "Comment 1"},
    )
    client.post(
        f"/api/v1/tasks/{task['id']}/comments?author_id={uid}",
        json={"body": "Comment 2"},
    )
    resp = client.get(f"/api/v1/tasks/{task['id']}/comments")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
