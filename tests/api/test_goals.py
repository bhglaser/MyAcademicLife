"""Tests for the goals and milestones API."""


def test_create_goal_with_milestones(client):
    resp = client.post(
        "/api/goals/",
        json={"title": "Publish 3 papers", "timeframe": "yearly"},
    )
    assert resp.status_code == 201
    gid = resp.json()["id"]

    resp = client.post(
        f"/api/goals/{gid}/milestones",
        json={"title": "Submit first paper", "goal_id": gid},
    )
    assert resp.status_code == 201

    resp = client.get(f"/api/goals/{gid}/milestones")
    assert len(resp.json()) == 1


def test_complete_milestone(client):
    resp = client.post(
        "/api/goals/",
        json={"title": "Learn Rust", "timeframe": "semester"},
    )
    gid = resp.json()["id"]

    resp = client.post(
        f"/api/goals/{gid}/milestones",
        json={"title": "Finish the book", "goal_id": gid},
    )
    msid = resp.json()["id"]

    resp = client.patch(f"/api/goals/milestones/{msid}", json={"is_complete": True})
    assert resp.status_code == 200
    assert resp.json()["is_complete"] is True
    assert resp.json()["completed_date"] is not None
