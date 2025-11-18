import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# Save initial activities state
import copy
initial_activities = copy.deepcopy(activities)

import pytest

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset activities before each test
    for k in initial_activities:
        activities[k]["participants"] = initial_activities[k]["participants"].copy()

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_for_activity():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Ensure not already signed up
    client.post(f"/activities/{activity}/unregister?email={email}")
    response = client.post(f"/activities/{activity}/signup", data={"email": email})
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    # Try signing up again (should fail)
    response2 = client.post(f"/activities/{activity}/signup", data={"email": email})
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]

def test_unregister_participant():
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Ensure signed up
    signup_response = client.post(f"/activities/{activity}/signup?email={email}")
    print(f"DEBUG: signup response: {signup_response.status_code}, {signup_response.json()}")
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    print(f"DEBUG: unregister response: {response.status_code}, {response.json()}")
    assert response.status_code == 200
    assert f"Removed {email}" in response.json()["message"]
    # Try unregistering again (should fail)
    response2 = client.post(f"/activities/{activity}/unregister?email={email}")
    print(f"DEBUG: unregister again response: {response2.status_code}, {response2.json()}")
    assert response2.status_code == 400
    assert "not registered" in response2.json()["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_invalid_activity():
    response = client.post("/activities/Nonexistent/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
