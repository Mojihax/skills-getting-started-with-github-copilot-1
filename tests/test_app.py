from fastapi.testclient import TestClient
import pytest

from src import app as app_module


client = TestClient(app_module.app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Create a temporary activity to avoid modifying existing fixtures
    activity_name = "Test Activity"
    activities = app_module.activities
    activities[activity_name] = {
        "description": "Temporary activity for tests",
        "schedule": "Now",
        "max_participants": 3,
        "participants": [],
    }

    try:
        email = "tester@example.com"

        # Sign up should succeed
        signup = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup.status_code == 200
        assert email in activities[activity_name]["participants"]

        # Signing up again should fail with 400
        signup_again = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_again.status_code == 400

        # Unregister should succeed
        unregister = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister.status_code == 200
        assert email not in activities[activity_name]["participants"]

        # Unregistering again should fail
        unregister_again = client.delete(f"/activities/{activity_name}/unregister?email={email}")
        assert unregister_again.status_code == 400

    finally:
        # Clean up
        activities.pop(activity_name, None)
