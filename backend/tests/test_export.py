import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import ADMIN_USER, make_mock_db


@pytest.mark.asyncio
async def test_export_requires_admin():
    mock_db = make_mock_db()

    with patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": "test-user-uuid"}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/export/responses?form_id=form-uuid-1&format=csv",
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_export_csv_admin():
    mock_db = make_mock_db(ADMIN_USER)
    mock_db.table.return_value.execute.return_value = MagicMock(data=[])

    with patch("app.services.export_service.get_supabase", return_value=mock_db), \
         patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": ADMIN_USER["id"]}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get(
                "/export/responses?form_id=00000000-0000-0000-0000-000000000001&format=csv",
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code == 200
    assert "text/csv" in resp.headers.get("content-type", "")
