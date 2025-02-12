import uuid
from typing import List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.users import Users
from app.schema.user_schema import (
    UserCreateSchema,
    UserInDBSchema,
    UserUpdateSchema,
)


class CRUDUser(CRUDBase[Users, UserCreateSchema, UserUpdateSchema]):
    pass


crud_user = CRUDUser(Users)
