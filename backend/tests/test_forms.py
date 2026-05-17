import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import decode_jwt
from tests.conftest import ADMIN_USER, PARTICIPANT_USER, TEST_FORM, TEST_QUESTION, make_mock_db


def mock_auth(user):
    def _get_current_user():
        return user
    return _get_current_user


@pytest.mark.asyncio
async def test_list_forms_participant_sees_active_only():
    mock_db = make_mock_db(PARTICIPANT_USER)
    mock_db.table.return_value.execute.return_value = MagicMock(data=[TEST_FORM])

    with patch("app.routers.forms.get_supabase", return_value=mock_db), \
         patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": PARTICIPANT_USER["id"]}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/forms", headers={"Authorization": "Bearer faketoken"})

    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_form_admin_only():
    mock_db = make_mock_db(PARTICIPANT_USER)

    with patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": PARTICIPANT_USER["id"]}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/forms",
                json={"title": "New Form", "questions": []},
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_form_as_admin():
    mock_db = make_mock_db(ADMIN_USER)
    created_form = {**TEST_FORM, "id": "new-form-uuid"}
    mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[created_form])

    with patch("app.routers.forms.get_supabase", return_value=mock_db), \
         patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": ADMIN_USER["id"]}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/forms",
                json={"title": "New Form", "questions": []},
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code == 201
