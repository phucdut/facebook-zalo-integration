import os
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.common import util
from app.common.enum.image_url import ImageUrl
from app.common.logger import setup_logger
from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.db import base  # noqa: F401
from app.db.base_class import Base
from app.models import Users
from app.schema import UserCreateSchema, UserInDBSchema

engine = create_engine(
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)


def init_db():

    # Create all tables for Base
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        crud_models = [
            crud_user,
        ]

    if not any(session.query(crud.model).count() for crud in crud_models):
        admin = crud_user.create(
            db=session,
            obj_in=UserInDBSchema(
                id=uuid.uuid4(),
                role="admin",
                display_name="admin123",
                password_hash=util.hash("admin"),
                email="admin@admin.com",
                avatar_url=ImageUrl.DEFAULT_IMAGE_USER,
                is_verified=True,
                verification_code=None,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                deleted_at=None,
            ),
        )
