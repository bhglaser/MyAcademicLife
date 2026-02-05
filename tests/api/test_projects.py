"""Tests for the research projects API."""


def test_create_and_list_projects(client):
    resp = client.post("/api/projects/", json={"title": "My Research"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Research"
    assert data["status"] == "active"

    resp = client.get("/api/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_project(client):
    resp = client.post("/api/projects/", json={"title": "P1"})
    pid = resp.json()["id"]

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "P1"


def test_update_project(client):
    resp = client.post("/api/projects/", json={"title": "Old"})
    pid = resp.json()["id"]

    resp = client.patch(f"/api/projects/{pid}", json={"title": "New"})
    assert resp.status_code == 200
    assert resp.json()["title"] == "New"


def test_delete_project(client):
    resp = client.post("/api/projects/", json={"title": "Temp"})
    pid = resp.json()["id"]

    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 204

    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 404
