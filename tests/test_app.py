"""
Tests for the Mergington High School API
Using the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest
from httpx import AsyncClient
from src.app import app, activities


@pytest.fixture
async def client():
    """Fixture providing an async HTTP client for the FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to known state before each test."""
    initial_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        }
    }

    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


@pytest.mark.asyncio
async def test_get_activities_returns_expected_structure(client):
    """GET /activities should return 200 and include activity data."""
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = await client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert set(data["Chess Club"].keys()) == expected_keys
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


@pytest.mark.asyncio
async def test_signup_for_activity_success(client):
    """POST /activities/{activity_name}/signup should add a new participant."""
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"

    # Act
    response = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


@pytest.mark.asyncio
async def test_signup_duplicate_participant_rejected(client):
    """Duplicate signup should return 400."""
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = await client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


@pytest.mark.asyncio
async def test_remove_participant_success(client):
    """DELETE /activities/{activity_name}/participants should remove an existing participant."""
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"

    # Act
    response = await client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove}
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in activities[activity_name]["participants"]


@pytest.mark.asyncio
async def test_remove_nonexistent_participant_rejected(client):
    """Removing a nonexistent participant should return 404."""
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "nonexistent@mergington.edu"

    # Act
    response = await client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email_to_remove}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in activity"
