import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app


PARTICIPANT_USER = {
    "id": "test-user-uuid",
    "dni": "12345678",
    "full_name": "Test Participant",
    "emails": ["test@example.com"],
    "primary_email": "test@example.com",
    "phone": None,
    "role": "participant",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}

ADMIN_USER = {
    **PARTICIPANT_USER,
    "id": "admin-user-uuid",
    "dni": "87654321",
    "full_name": "Admin User",
    "role": "admin",
}

TEST_FORM = {
    "id": "form-uuid-1",
    "title": "Test Form",
    "description": "A test form",
    "is_active": True,
    "opens_at": None,
    "closes_at": None,
    "created_by": "admin-user-uuid",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-01-01T00:00:00Z",
}

TEST_QUESTION = {
    "id": "question-uuid-1",
    "form_id": "form-uuid-1",
    "order_index": 0,
    "label": "What is your name?",
    "type": "short_text",
    "required": True,
    "options": None,
    "created_at": "2026-01-01T00:00:00Z",
}

TEST_SUBMISSION = {
    "id": "submission-uuid-1",
    "form_id": "form-uuid-1",
    "user_id": "test-user-uuid",
    "submitted_at": "2026-01-15T10:00:00Z",
    "last_edited_at": None,
    "edit_count": 0,
    "admin_notified_of_edit": False,
}


def make_mock_db(user=PARTICIPANT_USER):
    mock = MagicMock()
    table = MagicMock()
    mock.table.return_value = table
    table.select.return_value = table
    table.insert.return_value = table
    table.update.return_value = table
    table.delete.return_value = table
    table.eq.return_value = table
    table.neq.return_value = table
    table.or_.return_value = table
    table.gte.return_value = table
    table.lte.return_value = table
    table.gt.return_value = table
    table.lt.return_value = table
    table.is_.return_value = table
    table.order.return_value = table
    table.single.return_value = table
    table.execute.return_value = MagicMock(data=[user])
    return mock


@pytest.fixture
def participant_token():
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"


@pytest.fixture
def admin_token():
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.admin"


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
