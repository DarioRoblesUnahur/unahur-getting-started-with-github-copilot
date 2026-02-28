"""
Test suite for the High School Management System API

Tests are structured using the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

# Preserve the initial state for test resets
_INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the global activities dict before each test."""
    app_module.activities = copy.deepcopy(_INITIAL_ACTIVITIES)
    yield


def test_get_activities_returns_all():
    """Test that GET /activities returns all available activities."""
    # Arrange: none (state already reset by fixture)
    
    # Act
    resp = client.get("/activities")
    
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_contains_required_fields():
    """Test that each activity contains required metadata."""
    # Arrange
    # Act
    resp = client.get("/activities")
    
    # Assert
    assert resp.status_code == 200
    activities = resp.json()
    
    for activity_name, activity_data in activities.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    email = "new@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert resp.status_code == 200
    result = resp.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_email():
    """Test that duplicate signup is prevented."""
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity():
    """Test signup fails when activity doesn't exist."""
    # Arrange
    # Act
    resp = client.post(
        "/activities/NoSuchActivity/signup",
        params={"email": "test@mergington.edu"}
    )
    
    # Assert
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]


def test_signup_email_normalization():
    """Test that email signup handles case and whitespace variations."""
    # Arrange
    weird_email = "  NEW_USER@MERGINGTON.EDU  "
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": weird_email}
    )
    
    # Assert
    assert resp.status_code == 200
    # Verify the normalized email was stored
    stored_emails = app_module.activities[activity_name]["participants"]
    normalized_email = weird_email.strip().lower()
    assert normalized_email in stored_emails


def test_signup_duplicate_with_different_case():
    """Test that duplicate detection works across case variations."""
    # Arrange
    original_email = "michael@mergington.edu"
    weird_case_email = "MICHAEL@MERGINGTON.EDU"
    activity_name = "Chess Club"
    
    # Act: try to sign up with different case
    resp = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": weird_case_email}
    )
    
    # Assert: should fail due to case-insensitive duplicate check
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]


def test_withdraw_success():
    """Test successful withdrawal from an activity."""
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/withdraw",
        params={"email": email}
    )
    
    # Assert
    assert resp.status_code == 200
    result = resp.json()
    assert "Removed" in result["message"]
    assert email not in app_module.activities[activity_name]["participants"]


def test_withdraw_not_signed_up():
    """Test that withdrawal fails when student is not signed up."""
    # Arrange
    email = "not_enrolled@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/withdraw",
        params={"email": email}
    )
    
    # Assert
    assert resp.status_code == 400
    assert "Student not signed up for this activity" in resp.json()["detail"]


def test_withdraw_nonexistent_activity():
    """Test withdrawal fails for non-existent activity."""
    # Arrange
    # Act
    resp = client.post(
        "/activities/NoSuchActivity/withdraw",
        params={"email": "test@mergington.edu"}
    )
    
    # Assert
    assert resp.status_code == 404
    assert "Activity not found" in resp.json()["detail"]


def test_withdraw_email_normalization():
    """Test that email withdrawal handles case and whitespace variations."""
    # Arrange
    original_email = "michael@mergington.edu"
    weird_email = "  MICHAEL@MERGINGTON.EDU  "
    activity_name = "Chess Club"
    
    # Act
    resp = client.post(
        f"/activities/{activity_name}/withdraw",
        params={"email": weird_email}
    )
    
    # Assert
    assert resp.status_code == 200
    assert original_email not in app_module.activities[activity_name]["participants"]


def test_signup_then_withdraw_roundtrip():
    """Test full cycle: signup and then withdraw."""
    # Arrange
    email = "roundtrip@mergington.edu"
    activity_name = "Chess Club"
    
    # Act: Sign up
    signup_resp = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # Assert: Signup successful
    assert signup_resp.status_code == 200
    assert email in app_module.activities[activity_name]["participants"]
    
    # Act: Withdraw
    withdraw_resp = client.post(
        f"/activities/{activity_name}/withdraw",
        params={"email": email}
    )
    
    # Assert: Withdrawal successful
    assert withdraw_resp.status_code == 200
    assert email not in app_module.activities[activity_name]["participants"]


def test_multiple_signups_same_user_different_activities():
    """Test that a user can sign up for multiple different activities."""
    # Arrange
    email = "multi@mergington.edu"
    
    # Act: Sign up for Chess Club
    resp1 = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    
    # Act: Sign up for Programming Class
    resp2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email}
    )
    
    # Assert: Both signups successful
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert email in app_module.activities["Chess Club"]["participants"]
    assert email in app_module.activities["Programming Class"]["participants"]


def test_participant_count_consistency():
    """Test that participant counts match the actual participant lists."""
    # Arrange
    # Act
    resp = client.get("/activities")
    
    # Assert
    assert resp.status_code == 200
    activities = resp.json()
    
    for activity_name, activity_data in activities.items():
        actual_count = len(activity_data["participants"])
        # Ensure counts are reasonable
        assert actual_count <= activity_data["max_participants"]
        assert actual_count >= 0
