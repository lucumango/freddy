import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import PARTICIPANT_USER, ADMIN_USER, make_mock_db


@pytest.mark.asyncio
async def test_login_success():
    mock_db = make_mock_db()
    mock_db.table.return_value.single.return_value.execute.return_value = MagicMock(
        data={"id": PARTICIPANT_USER["id"], "role": "participant"}
    )
    mock_auth_user = MagicMock()
    mock_auth_user.user.email = "test@example.com"
    mock_db.auth.admin.get_user_by_id.return_value = mock_auth_user

    mock_session = MagicMock()
    mock_session.session.access_token = "fake_token"
    mock_anon = MagicMock()
    mock_anon.auth.sign_in_with_password.return_value = mock_session

    with patch("app.routers.auth.get_supabase", return_value=mock_db), \
         patch("app.routers.auth.get_supabase_anon", return_value=mock_anon):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/auth/login", json={"dni": "12345678", "password": "pass"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["access_token"] == "fake_token"
    assert data["role"] == "participant"


@pytest.mark.asyncio
async def test_login_invalid_dni():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/login", json={"dni": "1234", "password": "pass"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_credentials():
    mock_db = make_mock_db()
    mock_db.table.return_value.single.return_value.execute.return_value = MagicMock(data=None)

    with patch("app.routers.auth.get_supabase", return_value=mock_db), \
         patch("app.routers.auth.get_supabase_anon", return_value=MagicMock()):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/auth/login", json={"dni": "12345678", "password": "wrong"})

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_link_email_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/auth/link-email", json={"email": "new@example.com"})
    assert resp.status_code == 403
