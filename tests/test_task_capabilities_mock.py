"""Tests for newly mocked task capabilities.

NOTE:
- test_clone_done_task_should_reset_status_to_todo is EXPECTED TO FAIL due to Bug #3
- test_defer_task_should_shift_due_date_by_days is EXPECTED TO FAIL due to Bug #4
- test_reassign_should_preserve_priority is EXPECTED TO FAIL due to Bug #5
- test_bulk_cancel_should_not_touch_other_users_tasks is EXPECTED TO FAIL due to Bug #6
"""

from datetime import datetime, timedelta


def _create_task(client, owner_id, **overrides):
    payload = {
        "title": "Prepare release notes",
        "description": "Compile all release highlights",
        "priority": "medium",
    }
    payload.update(overrides)
    resp = client.post(f"/api/v1/tasks/?owner_id={owner_id}", json=payload)
    assert resp.status_code == 201
    return resp.json()


def _create_user(client, username, email):
    resp = client.post(
        "/api/v1/users/",
        json={"username": username, "email": email, "password": "securepass123"},
    )
    assert resp.status_code == 201
    return resp.json()


def test_clone_task_creates_new_task(client, sample_user):
    task = _create_task(client, sample_user["id"])
    resp = client.post(f"/api/v1/tasks/{task['id']}/clone")
    assert resp.status_code == 201

    clone = resp.json()
    assert clone["id"] != task["id"]
    assert clone["title"].startswith("Copy of ")
    assert clone["description"] == task["description"]
    assert clone["priority"] == task["priority"]


def test_clone_done_task_should_reset_status_to_todo(client, sample_user):
    """Cloned tasks should always start as todo.
    This test FAILS due to Bug #3 (status copied from source task)."""
    task = _create_task(client, sample_user["id"])

    done_resp = client.patch(f"/api/v1/tasks/{task['id']}", json={"status": "done"})
    assert done_resp.status_code == 200

    clone_resp = client.post(f"/api/v1/tasks/{task['id']}/clone")
    assert clone_resp.status_code == 201

    clone = clone_resp.json()
    assert clone["status"] == "todo", (
        "Cloned tasks must reset status to todo even if source is done"
    )


def test_defer_task_with_existing_due_date(client, sample_user):
    future_due = datetime.utcnow() + timedelta(days=2)
    task = _create_task(
        client,
        sample_user["id"],
        due_date=future_due.isoformat(),
    )

    resp = client.post(f"/api/v1/tasks/{task['id']}/defer?days=1")
    assert resp.status_code == 200
    deferred = resp.json()
    assert deferred["due_date"] is not None


def test_defer_task_should_shift_due_date_by_days(client, sample_user):
    """Deferral should add whole days to due_date.
    This test FAILS due to Bug #4 (hours used instead of days)."""
    start_due = datetime.utcnow() + timedelta(days=3)
    task = _create_task(
        client,
        sample_user["id"],
        due_date=start_due.isoformat(),
    )

    resp = client.post(f"/api/v1/tasks/{task['id']}/defer?days=2")
    assert resp.status_code == 200

    updated_due = datetime.fromisoformat(resp.json()["due_date"])
    expected_due = datetime.fromisoformat(task["due_date"]) + timedelta(days=2)

    delta = abs((updated_due - expected_due).total_seconds())
    assert delta < 2, (
        "Due date should be deferred by 2 full days"
    )


def test_reassign_task_changes_owner(client, sample_user):
    target_user = _create_user(client, "bob", "bob@example.com")
    task = _create_task(client, sample_user["id"], priority="high")

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/reassign?new_owner_id={target_user['id']}"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["owner_id"] == target_user["id"]


def test_reassign_should_preserve_priority(client, sample_user):
    """Reassign should not alter priority.
    This test FAILS due to Bug #5 (priority forced to low)."""
    target_user = _create_user(client, "carol", "carol@example.com")
    task = _create_task(client, sample_user["id"], priority="high")

    resp = client.post(
        f"/api/v1/tasks/{task['id']}/reassign?new_owner_id={target_user['id']}"
    )
    assert resp.status_code == 200
    assert resp.json()["priority"] == "high", (
        "Priority should remain unchanged after reassignment"
    )


def test_bulk_cancel_returns_count(client, sample_user):
    uid = sample_user["id"]
    _create_task(client, uid, title="Owner task 1")
    _create_task(client, uid, title="Owner task 2")

    resp = client.post(f"/api/v1/tasks/bulk/cancel?owner_id={uid}")
    assert resp.status_code == 200
    assert resp.json()["cancelled_count"] >= 2


def test_bulk_cancel_should_not_touch_other_users_tasks(client, sample_user):
    """Bulk cancel should only affect the selected owner.
    This test FAILS due to Bug #6 (missing owner filter)."""
    owner_a = sample_user
    owner_b = _create_user(client, "dave", "dave@example.com")

    _create_task(client, owner_a["id"], title="A task")
    b_task = _create_task(client, owner_b["id"], title="B task")

    cancel_resp = client.post(f"/api/v1/tasks/bulk/cancel?owner_id={owner_a['id']}")
    assert cancel_resp.status_code == 200

    b_task_resp = client.get(f"/api/v1/tasks/{b_task['id']}")
    assert b_task_resp.status_code == 200
    assert b_task_resp.json()["status"] == "todo", (
        "Bulk cancel for owner A should not cancel owner B tasks"
    )
