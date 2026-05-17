from fastapi import APIRouter, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_supabase, get_supabase_anon
from app.middleware.auth_middleware import get_current_user, require_admin
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest,
    LinkEmailRequest, LinkPhoneRequest, ChangePasswordRequest,
)
from fastapi import Depends

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    db_anon = get_supabase_anon()
    db = get_supabase()

    user_row = db.table("users").select("id, role").eq("dni", body.dni).single().execute()
    if not user_row.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid DNI or password")

    user_id = user_row.data["id"]
    user_auth = db.auth.admin.get_user_by_id(user_id)
    if not user_auth.user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid DNI or password")

    email = user_auth.user.email
    try:
        session = db_anon.auth.sign_in_with_password({"email": email, "password": body.password})
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid DNI or password")

    return LoginResponse(
        access_token=session.session.access_token,
        user_id=user_id,
        role=user_row.data["role"],
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, admin: dict = Depends(require_admin)):
    db = get_supabase()

    existing = db.table("users").select("id").eq("dni", body.dni).execute()
    if existing.data:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="DNI already registered")

    auth_user = db.auth.admin.create_user({
        "email": body.email,
        "password": body.password,
        "email_confirm": True,
    })
    if not auth_user.user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create auth user")

    db.table("users").insert({
        "id": auth_user.user.id,
        "dni": body.dni,
        "full_name": body.full_name,
        "emails": [body.email],
        "primary_email": body.email,
        "role": "participant",
    }).execute()

    return {"user_id": auth_user.user.id, "message": "User registered"}


@router.post("/link-email")
async def link_email(body: LinkEmailRequest, current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    emails = current_user.get("emails") or []
    if body.email in emails:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already linked")
    emails.append(body.email)
    db.table("users").update({"emails": emails}).eq("id", current_user["id"]).execute()
    return {"emails": emails}


@router.post("/link-phone")
async def link_phone(body: LinkPhoneRequest, current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    db.table("users").update({"phone": body.phone}).eq("id", current_user["id"]).execute()
    return {"phone": body.phone}


@router.post("/change-password")
async def change_password(body: ChangePasswordRequest, current_user: dict = Depends(get_current_user)):
    db = get_supabase()
    db.auth.admin.update_user_by_id(current_user["id"], {"password": body.new_password})
    return {"message": "Password updated"}
