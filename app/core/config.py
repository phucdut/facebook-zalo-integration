import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import PostgresDsn, field_validator, validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    ENV: str = os.getenv("ENV") or "development"
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")

    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER")
    POSTGRES_PORT: int = os.environ.get("POSTGRES_PORT")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB")

    MY_VERIFY_TOKEN: str = os.environ.get("MY_VERIFY_TOKEN")
    PAGE_ACCESS_TOKEN: str = os.environ.get("PAGE_ACCESS_TOKEN")

    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    FACEBOOK_URL: str = os.environ.get("FACEBOOK_URL")
    AI_URL: str = os.environ.get("AI_URL")

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(
        cls, v: Optional[str], info: FieldValidationInfo
    ) -> Any:
        if isinstance(v, str):
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_SERVER"),
            port=info.data.get("POSTGRES_PORT"),
            path=info.data.get("POSTGRES_DB"),
        )

    class Config:
        case_sensitive = True


settings = Settings()
