from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import logging

from app.core.database import get_supabase
from app.routers import auth, forms, questions, responses, users, export, reports
from app.services.notification_service import send_deadline_warning, was_notified_today

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)


def _auto_open_close_forms():
    db = get_supabase()
    now = datetime.now(timezone.utc).isoformat()
    db.table("forms").update({"is_active": True, "updated_at": now}).lte("opens_at", now).eq("is_active", False).is_("closes_at", "null").execute()
    db.table("forms").update({"is_active": True, "updated_at": now}).lte("opens_at", now).gt("closes_at", now).eq("is_active", False).execute()
    db.table("forms").update({"is_active": False, "updated_at": now}).lte("closes_at", now).eq("is_active", True).execute()


def _send_deadline_warnings():
    db = get_supabase()
    now = datetime.now(timezone.utc)
    in_24h = (now + timedelta(hours=24)).isoformat()

    closing_forms = (
        db.table("forms")
        .select("id, title, closes_at")
        .eq("is_active", True)
        .gte("closes_at", now.isoformat())
        .lte("closes_at", in_24h)
        .execute()
        .data
    )

    for form in closing_forms:
        users = db.table("users").select("id, full_name, primary_email, emails").eq("role", "participant").execute().data
        submissions = db.table("submissions").select("user_id").eq("form_id", form["id"]).execute().data
        submitted_ids = {s["user_id"] for s in submissions}

        closes_dt = datetime.fromisoformat(form["closes_at"].replace("Z", "+00:00"))
        for user in users:
            if user["id"] in submitted_ids:
                continue
            if was_notified_today(user["id"], "deadline"):
                continue
            email = user.get("primary_email") or (user.get("emails") or [""])[0]
            if email:
                send_deadline_warning(user["id"], email, user.get("full_name", ""), form["title"], closes_dt)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(_auto_open_close_forms, "interval", hours=1, id="auto_forms")
    scheduler.add_job(
        _send_deadline_warnings,
        CronTrigger(hour=14, minute=0, timezone=pytz.utc),  # 9am Lima (UTC-5)
        id="deadline_warnings",
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="QHub Course Management API",
    description="Platform for managing forms, responses, and participants for QuantumHub Peru",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(forms.router)
app.include_router(questions.router)
app.include_router(responses.router)
app.include_router(users.router)
app.include_router(export.router)
app.include_router(reports.router)


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "project": "QHub Course Management API", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
