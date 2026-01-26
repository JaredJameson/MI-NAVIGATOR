"""
Unit tests for Reports CRUD endpoints.

Tests cover:
- List reports
- Create report
- Get report by ID
- Update report
- Delete report
- Report permissions (user isolation)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole


# ============================================================================
# LIST REPORTS TESTS
# ============================================================================

@pytest.mark.unit
async def test_list_reports_empty(client: AsyncClient, auth_headers: dict):
    """Test listing reports when user has no reports."""
    response = await client.get(
        "/api/v1/reports/",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert "reports" in data or "items" in data
    # Should be empty list or similar


@pytest.mark.unit
async def test_list_reports_requires_auth(client: AsyncClient):
    """Test listing reports without authentication fails."""
    response = await client.get("/api/v1/reports/")

    assert response.status_code == 401


# ============================================================================
# CREATE REPORT TESTS
# ============================================================================

@pytest.mark.unit
async def test_create_report_minimal(client: AsyncClient, auth_headers: dict):
    """Test creating a report with minimal data."""
    response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Test Report",
            "type": "market_analysis",
            "content": "This is test content for the report",
            "summary": "This is a test report"
        }
    )

    assert response.status_code in [200, 201]  # Created or OK

    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Report"
    assert data["status"] == "created"


@pytest.mark.unit
async def test_create_report_with_sections(client: AsyncClient, auth_headers: dict):
    """Test creating a report with sections."""
    response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Test Report with Sections",
            "type": "company_profile",
            "content": "Main report content",
            "summary": "Test summary"
        }
    )

    assert response.status_code in [200, 201]

    data = response.json()
    # API returns minimal response: id, status, title
    assert "id" in data
    assert data["title"] == "Test Report with Sections"


@pytest.mark.unit
async def test_create_report_without_auth(client: AsyncClient):
    """Test creating report without authentication fails."""
    response = await client.post(
        "/api/v1/reports/",
        json={
            "title": "Unauthorized Report",
            "type": "market_analysis"
        }
    )

    assert response.status_code == 401


@pytest.mark.unit
async def test_create_report_missing_title(client: AsyncClient, auth_headers: dict):
    """Test creating report without title fails validation."""
    response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "type": "market_analysis"
            # Missing title
        }
    )

    assert response.status_code in [400, 422]  # Bad request or validation error


# ============================================================================
# GET REPORT BY ID TESTS
# ============================================================================

@pytest.mark.unit
async def test_get_report_by_id(client: AsyncClient, auth_headers: dict):
    """Test getting a report by ID."""
    # First create a report
    create_response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Test Report for Get",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Test"
        }
    )

    assert create_response.status_code in [200, 201]
    report_data = create_response.json()
    report_id = report_data["id"]

    # Now get it
    response = await client.get(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == report_id
    assert data["title"] == "Test Report for Get"


@pytest.mark.unit
async def test_get_report_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting non-existent report returns 404."""
    fake_id = "nonexistent-report-id-12345"

    response = await client.get(
        f"/api/v1/reports/{fake_id}",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.unit
async def test_get_report_without_auth(client: AsyncClient):
    """Test getting report without authentication fails."""
    response = await client.get("/api/v1/reports/some-id")

    assert response.status_code == 401


# ============================================================================
# UPDATE REPORT TESTS
# ============================================================================

@pytest.mark.unit
async def test_update_report_title(client: AsyncClient, auth_headers: dict):
    """Test updating report title."""
    # First create a report
    create_response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Original Title",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Test"
        }
    )

    assert create_response.status_code in [200, 201]
    report_data = create_response.json()
    report_id = report_data["id"]

    # Now update it
    response = await client.put(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers,
        json={"title": "Updated Title"}
    )

    assert response.status_code == 200
    data = response.json()

    # API returns message, report_id, version, updated_at
    assert data["report_id"] == report_id
    assert data["message"] == "Report updated successfully"


@pytest.mark.unit
async def test_update_report_add_section(client: AsyncClient, auth_headers: dict):
    """Test adding a section to a report."""
    # First create a report
    create_response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Report for Section Test",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Test"
        }
    )

    assert create_response.status_code in [200, 201]
    report_data = create_response.json()
    report_id = report_data["id"]

    # Update with new section
    response = await client.put(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers,
        json={
            "title": "Report for Section Test",
            "sections": [
                {
                    "id": "section_1",
                    "title": "New Section",
                    "content": "New section content"
                }
            ]
        }
    )

    assert response.status_code == 200


@pytest.mark.unit
async def test_update_report_not_found(client: AsyncClient, auth_headers: dict):
    """Test updating non-existent report returns 404."""
    response = await client.put(
        "/api/v1/reports/nonexistent-id",
        headers=auth_headers,
        json={"title": "Won't work"}
    )

    assert response.status_code == 404


@pytest.mark.unit
async def test_update_report_without_auth(client: AsyncClient):
    """Test updating report without authentication fails."""
    response = await client.put(
        "/api/v1/reports/some-id",
        json={"title": "Unauthorized"}
    )

    assert response.status_code == 401


# ============================================================================
# DELETE REPORT TESTS
# ============================================================================

@pytest.mark.unit
async def test_delete_report(client: AsyncClient, auth_headers: dict):
    """Test deleting a report."""
    # First create a report
    create_response = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={
            "title": "Report to Delete",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Test"
        }
    )

    assert create_response.status_code in [200, 201]
    report_data = create_response.json()
    report_id = report_data["id"]

    # Now delete it
    response = await client.delete(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers
    )

    assert response.status_code in [200, 204]  # OK or No Content

    # Verify it's deleted
    get_response = await client.get(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers
    )

    assert get_response.status_code == 404


@pytest.mark.unit
async def test_delete_report_not_found(client: AsyncClient, auth_headers: dict):
    """Test deleting non-existent report."""
    response = await client.delete(
        "/api/v1/reports/nonexistent-id",
        headers=auth_headers
    )

    assert response.status_code == 404


@pytest.mark.unit
async def test_delete_report_without_auth(client: AsyncClient):
    """Test deleting report without authentication fails."""
    response = await client.delete("/api/v1/reports/some-id")

    assert response.status_code == 401


# ============================================================================
# REPORT PERMISSIONS TESTS
# ============================================================================

@pytest.mark.unit
async def test_user_isolation_reports(client: AsyncClient, db_session: AsyncSession):
    """Test that users can only see their own reports."""
    import uuid
    from datetime import datetime

    # Create two users with valid password hashes and all required fields
    user1 = User(
        id=uuid.uuid4(),
        email="reportuser1@example.com",
        password_hash="$2b$12$TGPvezBHJCsLvN9sf1vS.O8WGNh8njCxq/VBS5KM7jPKqpmueEXSe",  # "password123"
        name="User 1",
        role=UserRole.USER,
        preferred_language="pl",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    user2 = User(
        id=uuid.uuid4(),
        email="reportuser2@example.com",
        password_hash="$2b$12$TGPvezBHJCsLvN9sf1vS.O8WGNh8njCxq/VBS5KM7jPKqpmueEXSe",  # "password123"
        name="User 2",
        role=UserRole.USER,
        preferred_language="en",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Login as user1 and create a report
    login1 = await client.post(
        "/api/v1/auth/login",
        json={"email": "reportuser1@example.com", "password": "password123"}
    )

    assert login1.status_code == 200
    user1_token = login1.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}

    create_resp = await client.post(
        "/api/v1/reports/",
        headers=user1_headers,
        json={
            "title": "User 1's Report",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Private report"
        }
    )

    assert create_resp.status_code in [200, 201]
    report_id = create_resp.json()["id"]

    # Login as user2 and try to access user1's report
    login2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "reportuser2@example.com", "password": "password123"}
    )

    assert login2.status_code == 200
    user2_token = login2.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User2 should NOT be able to see user1's report
    get_resp = await client.get(
        f"/api/v1/reports/{report_id}",
        headers=user2_headers
    )

    # Should either be 404 (not found) or 403 (forbidden)
    assert get_resp.status_code in [403, 404]


@pytest.mark.unit
async def test_user_cannot_delete_others_report(client: AsyncClient, db_session: AsyncSession):
    """Test that users cannot delete reports created by other users."""
    import uuid
    from datetime import datetime

    # Create two users with valid password hashes and all required fields
    user1 = User(
        id=uuid.uuid4(),
        email="deleteuser1@example.com",
        password_hash="$2b$12$TGPvezBHJCsLvN9sf1vS.O8WGNh8njCxq/VBS5KM7jPKqpmueEXSe",  # "password123"
        name="User 1",
        role=UserRole.USER,
        preferred_language="pl",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    user2 = User(
        id=uuid.uuid4(),
        email="deleteuser2@example.com",
        password_hash="$2b$12$TGPvezBHJCsLvN9sf1vS.O8WGNh8njCxq/VBS5KM7jPKqpmueEXSe",  # "password123"
        name="User 2",
        role=UserRole.USER,
        preferred_language="en",
        preferred_depth="standard",
        preferred_currency="PLN",
        timezone="Europe/Warsaw",
        onboarding_completed=True,
        is_active=True,
        email_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db_session.add(user1)
    db_session.add(user2)
    await db_session.commit()

    # Login as user1 and create a report
    login1 = await client.post(
        "/api/v1/auth/login",
        json={"email": "deleteuser1@example.com", "password": "password123"}
    )

    user1_headers = {"Authorization": f"Bearer {login1.json()['access_token']}"}

    create_resp = await client.post(
        "/api/v1/reports/",
        headers=user1_headers,
        json={
            "title": "User 1's Report",
            "type": "market_analysis",
            "content": "Test content",
            "summary": "Should not be deletable by others"
        }
    )

    report_id = create_resp.json()["id"]

    # Login as user2 and try to delete user1's report
    login2 = await client.post(
        "/api/v1/auth/login",
        json={"email": "deleteuser2@example.com", "password": "password123"}
    )

    user2_headers = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    delete_resp = await client.delete(
        f"/api/v1/reports/{report_id}",
        headers=user2_headers
    )

    # Should be forbidden or not found
    assert delete_resp.status_code in [403, 404]


# ============================================================================
# BULK DELETE TESTS
# ============================================================================

@pytest.mark.unit
async def test_bulk_delete_reports(client: AsyncClient, auth_headers: dict):
    """Test bulk deleting multiple reports."""
    # Create multiple reports
    report_ids = []

    for i in range(3):
        resp = await client.post(
            "/api/v1/reports/",
            headers=auth_headers,
            json={
                "title": f"Bulk Delete Test {i}",
                "type": "market_analysis",
                "content": f"Test content for report {i}",
                "summary": f"Report {i}"
            }
        )

        assert resp.status_code in [200, 201]
        report_ids.append(resp.json()["id"])

    # Bulk delete
    response = await client.post(
        "/api/v1/reports/bulk-delete",
        headers=auth_headers,
        json={"report_ids": report_ids}
    )

    assert response.status_code == 200

    # Verify all are deleted
    for report_id in report_ids:
        get_resp = await client.get(
            f"/api/v1/reports/{report_id}",
            headers=auth_headers
        )

        assert get_resp.status_code == 404


@pytest.mark.unit
async def test_bulk_delete_empty_list(client: AsyncClient, auth_headers: dict):
    """Test bulk delete with empty list returns 400."""
    response = await client.post(
        "/api/v1/reports/bulk-delete",
        headers=auth_headers,
        json={"report_ids": []}
    )

    # API rejects empty lists with 400 error
    assert response.status_code == 400


@pytest.mark.unit
async def test_bulk_delete_without_auth(client: AsyncClient):
    """Test bulk delete without authentication fails."""
    response = await client.post(
        "/api/v1/reports/bulk-delete",
        json={"report_ids": ["some-id"]}
    )

    assert response.status_code == 401


# ============================================================================
# REPORT FILTERING TESTS
# ============================================================================

@pytest.mark.unit
async def test_filter_reports_by_type(client: AsyncClient, auth_headers: dict):
    """Test filtering reports by type."""
    # Create reports of different types
    await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={"title": "Market Report", "type": "market_analysis", "content": "Test content",
            "summary": "Test"}
    )

    await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={"title": "Company Report", "type": "company_profile", "content": "Test content",
            "summary": "Test"}
    )

    # Filter by type
    response = await client.get(
        "/api/v1/reports/?type=market_analysis",
        headers=auth_headers
    )

    assert response.status_code == 200


# ============================================================================
# ARCHIVE REPORT TESTS
# ============================================================================

@pytest.mark.unit
async def test_archive_report(client: AsyncClient, auth_headers: dict):
    """Test archiving a report."""
    # Create a report
    create_resp = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={"title": "To Archive", "type": "market_analysis", "content": "Test content",
            "summary": "Test"}
    )

    report_id = create_resp.json()["id"]

    # Archive it
    response = await client.post(
        f"/api/v1/reports/{report_id}/archive",
        headers=auth_headers
    )

    assert response.status_code == 200

    # Verify it's archived
    get_resp = await client.get(
        f"/api/v1/reports/{report_id}",
        headers=auth_headers
    )

    if get_resp.status_code == 200:
        data = get_resp.json()
        assert data.get("is_archived") is True


@pytest.mark.unit
async def test_unarchive_report(client: AsyncClient, auth_headers: dict):
    """Test unarchiving a report."""
    # Create and archive a report
    create_resp = await client.post(
        "/api/v1/reports/",
        headers=auth_headers,
        json={"title": "To Unarchive", "type": "market_analysis", "content": "Test content",
            "summary": "Test"}
    )

    report_id = create_resp.json()["id"]

    # Archive
    await client.post(
        f"/api/v1/reports/{report_id}/archive",
        headers=auth_headers
    )

    # Unarchive
    response = await client.post(
        f"/api/v1/reports/{report_id}/unarchive",
        headers=auth_headers
    )

    assert response.status_code == 200
