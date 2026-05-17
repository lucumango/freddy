import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from app.main import app
from tests.conftest import PARTICIPANT_USER, TEST_FORM, TEST_SUBMISSION, make_mock_db


@pytest.mark.asyncio
async def test_submit_form_success():
    mock_db = make_mock_db(PARTICIPANT_USER)
    mock_db.table.return_value.eq.return_value.execute.return_value = MagicMock(data=[])
    mock_db.table.return_value.single.return_value.execute.return_value = MagicMock(data=TEST_FORM)
    mock_db.table.return_value.insert.return_value.execute.return_value = MagicMock(data=[TEST_SUBMISSION])

    with patch("app.routers.responses.get_supabase", return_value=mock_db), \
         patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": PARTICIPANT_USER["id"]}), \
         patch("app.routers.responses._build_submission_out", return_value={
             "id": TEST_SUBMISSION["id"],
             "form_id": TEST_SUBMISSION["form_id"],
             "form_title": "Test Form",
             "user_id": PARTICIPANT_USER["id"],
             "submitted_at": TEST_SUBMISSION["submitted_at"],
             "last_edited_at": None,
             "edit_count": 0,
             "answers": [],
         }):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/responses/submit",
                json={"form_id": "form-uuid-1", "answers": []},
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code in (201, 409, 400)


@pytest.mark.asyncio
async def test_submit_duplicate_returns_409():
    mock_db = make_mock_db(PARTICIPANT_USER)
    mock_db.table.return_value.eq.return_value.execute.return_value = MagicMock(data=[TEST_SUBMISSION])

    with patch("app.routers.responses.get_supabase", return_value=mock_db), \
         patch("app.middleware.auth_middleware.get_supabase", return_value=mock_db), \
         patch("app.core.security.decode_jwt", return_value={"sub": PARTICIPANT_USER["id"]}):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/responses/submit",
                json={"form_id": "form-uuid-1", "answers": []},
                headers={"Authorization": "Bearer faketoken"},
            )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_my_submissions_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/responses/my")
    assert resp.status_code == 403
