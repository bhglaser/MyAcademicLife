"""Tests for the deadlines API."""


def test_create_and_list_deadlines(client):
    resp = client.post(
        "/api/deadlines/",
        json={
            "title": "NeurIPS submission",
            "kind": "conference",
            "due_date": "2026-05-15T23:59:00",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "NeurIPS submission"
    assert data["kind"] == "conference"

    resp = client.get("/api/deadlines/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_update_deadline_status(client):
    resp = client.post(
        "/api/deadlines/",
        json={
            "title": "Grant proposal",
            "kind": "grant",
            "due_date": "2026-06-01T17:00:00",
        },
    )
    did = resp.json()["id"]

    resp = client.patch(f"/api/deadlines/{did}", json={"status": "submitted"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "submitted"
