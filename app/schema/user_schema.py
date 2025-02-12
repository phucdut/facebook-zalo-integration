import uuid
from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, EmailStr

from app.schema._soft_delete_schema import SoftDeleteSchema


class UserSignUpSchema(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


class UserSignInSchema(BaseModel):
    email: EmailStr
    password: str



class UserCreateSchema(UserSignUpSchema):
    email: EmailStr
    password_hash: str


class UserUpdateSchema(BaseModel):
    role: Optional[str] = None
    display_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    is_verified: Optional[bool] = None
    verification_code: Optional[str] = None


class UserInDBSchema(SoftDeleteSchema):
    ID: ClassVar[str] = "id"
    ROLE: ClassVar[str] = "role"
    DISPLAY_NAME: ClassVar[str] = "display_name"
    PASSWORD_HASH: ClassVar[str] = "password_hash"
    EMAIL: ClassVar[str] = "email"
    AVATAR_URL: ClassVar[str] = "avatar_url"
    IS_VERIFIED: ClassVar[str] = "is_verified"
    VERIFICATION_CODE: ClassVar[str] = "verification_code"

    id: uuid.UUID
    role: str
    display_name: str
    password_hash: str
    email: EmailStr
    avatar_url: str
    is_verified: bool
    verification_code: Optional[str]

    class Config:
        orm_mode = True


class UserResponseSchema(SoftDeleteSchema):
    ID: ClassVar[str] = "id"
    ROLE: ClassVar[str] = "role"
    DISPLAY_NAME: ClassVar[str] = "display_name"
    EMAIL: ClassVar[str] = "email"
    AVATAR_URL: ClassVar[str] = "avatar_url"
    IS_VERIFIED: ClassVar[str] = "is_verified"

    id: uuid.UUID
    role: str
    display_name: str
    email: EmailStr
    avatar_url: str
    is_verified: bool

    class Config:
        orm_mode = True


class UserAdminResponseSchema(SoftDeleteSchema):
    id: uuid.UUID
    role: str
    display_name: str
    email: EmailStr
    avatar_url: str
    is_verified: bool
    quantity_chatbot: int
    total_message: int
    total_token: int

    class Config:
        orm_mode = True


class UserDetailResponseSchema(SoftDeleteSchema):
    id: uuid.UUID
    package_id: uuid.UUID
    user_membership_id: uuid.UUID
    role: str
    display_name: str
    email: EmailStr
    avatar_url: str
    is_verified: bool
    package_title: str
    expire_at: datetime

    class Config:
        orm_mode = True


class UserFacebookResponseSchema(SoftDeleteSchema):
    id: uuid.UUID
    name: str
    phoneNumber: str
    time: str
    quantity: str
    createdAt: str

    class Config:
        orm_mode = True


class UserListOrganizationResponseSchema(UserResponseSchema, SoftDeleteSchema):
    user_role_in_org: str


class UserListStoreResponseSchema(UserResponseSchema, SoftDeleteSchema):
    user_role_in_store: str
