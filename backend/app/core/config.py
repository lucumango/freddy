from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    supabase_url: str
    supabase_publishable_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    resend_api_key: str
    resend_from_email: str = "noreply@qhubperu.com"
    resend_admin_emails: str = ""

    app_env: str = "development"
    app_secret_key: str = "change_me"

    @property
    def admin_email_list(self) -> List[str]:
        return [e.strip() for e in self.resend_admin_emails.split(",") if e.strip()]


settings = Settings()
