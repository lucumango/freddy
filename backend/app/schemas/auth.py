from pydantic import BaseModel, EmailStr, field_validator
import re


class LoginRequest(BaseModel):
    dni: str
    password: str

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, v: str) -> str:
        if not re.match(r"^\d{8}$", v):
            raise ValueError("DNI must be exactly 8 digits")
        return v


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RegisterRequest(BaseModel):
    dni: str
    full_name: str
    email: EmailStr
    password: str

    @field_validator("dni")
    @classmethod
    def validate_dni(cls, v: str) -> str:
        if not re.match(r"^\d{8}$", v):
            raise ValueError("DNI must be exactly 8 digits")
        return v


class LinkEmailRequest(BaseModel):
    email: EmailStr


class LinkPhoneRequest(BaseModel):
    phone: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
