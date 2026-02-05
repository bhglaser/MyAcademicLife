"""Tests for the tasks API."""


def test_create_and_complete_task(client):
    resp = client.post("/api/tasks/", json={"title": "Read paper X"})
    assert resp.status_code == 201
    tid = resp.json()["id"]

    resp = client.patch(f"/api/tasks/{tid}", json={"status": "done"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "done"
    assert data["completed_at"] is not None


def test_filter_tasks_by_status(client):
    client.post("/api/tasks/", json={"title": "Task A"})
    resp = client.post("/api/tasks/", json={"title": "Task B"})
    tid = resp.json()["id"]
    client.patch(f"/api/tasks/{tid}", json={"status": "done"})

    resp = client.get("/api/tasks/", params={"status": "todo"})
    assert len(resp.json()) == 1


def test_task_categories(client):
    resp = client.post(
        "/api/tasks/categories",
        json={"name": "Research", "color": "#3b82f6"},
    )
    assert resp.status_code == 201
    cid = resp.json()["id"]

    resp = client.post("/api/tasks/", json={"title": "Do thing", "category_id": cid})
    assert resp.status_code == 201
    assert resp.json()["category_id"] == cid
