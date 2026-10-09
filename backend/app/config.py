from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app.lockout import parse_tiers


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "inogov_user"
    db_password: str = "inogov_password"
    db_name: str = "inogov_db_dev"

    secret_key: str
    access_token_expire_minutes: int = 60
    lockout_tiers: str = "3:3,5:10,10:60"

    app_name: str = "inoGOV"
    copyright_name: str = "inoGOV"
    public_search: bool = True
    admin_otp_required: bool = True
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    password_reset_minutes: int = 60
    admin_link_hours: int = 24

    smtp_server: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@localhost"
    smtp_from_name: str = "inoGOV"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def lockout_tier_list(self) -> list[tuple[int, int]]:
        return parse_tiers(self.lockout_tiers)

    @property
    def database_url(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()
