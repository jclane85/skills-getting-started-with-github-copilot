"""
Tests for the High School Management System API using the
Arrange-Act-Assert (AAA) pattern.

Run with: pytest -q
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: snapshot the in-memory activities before each test
    original = copy.deepcopy(activities)
    yield
    # Assert / Teardown: restore original state so tests are isolated
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    # Arrange: none (server seeded)

    # Act
    resp = client.get("/activities")
    data = resp.json()

    # Assert
    assert resp.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity = "Chess Club"
    email = "testuser@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate_fails(client):
    # Arrange
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"].lower()


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity = "Nonexistent Club"

    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": "user@example.com"})

    # Assert
    assert resp.status_code == 404


def test_unregister_removes_participant(client):
    # Arrange
    activity = "Chess Club"
    participant = activities[activity]["participants"][0]
    assert participant in activities[activity]["participants"]

    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": participant})

    # Assert
    assert resp.status_code == 200
    assert participant not in activities[activity]["participants"]


def test_unregister_not_registered_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = "not-registered@example.com"
    assert email not in activities[activity]["participants"]

    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})

    # Assert
    assert resp.status_code == 400
    assert "not signed up" in resp.json()["detail"].lower()
