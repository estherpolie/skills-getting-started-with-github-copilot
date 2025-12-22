import os
import sys
from fastapi.testclient import TestClient

# Ensure src directory is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from app import app  # noqa: E402


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Expect at least one activity
    assert len(data) > 0


def test_signup_and_unregister_flow():
    # Pick an activity from the list
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    activity_name = next(iter(activities.keys()))

    test_email = "test_student@example.com"

    # Ensure not already registered (if so, try to remove first)
    if test_email in activities[activity_name]["participants"]:
        r = client.delete(f"/activities/{activity_name}/participants", params={"email": test_email})
        assert r.status_code == 200

    # Sign up the test student
    signup = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    assert signup.status_code == 200
    assert "Signed up" in signup.json().get("message", "")

    # Verify student now present
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    activities2 = resp2.json()
    assert test_email in activities2[activity_name]["participants"]

    # Unregister the student
    unreg = client.delete(f"/activities/{activity_name}/participants", params={"email": test_email})
    assert unreg.status_code == 200
    assert "Unregistered" in unreg.json().get("message", "")

    # Verify removed
    resp3 = client.get("/activities")
    assert resp3.status_code == 200
    activities3 = resp3.json()
    assert test_email not in activities3[activity_name]["participants"]
