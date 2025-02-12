from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Users(Base):
    __tablename__ = "users"

    role = Column(String, nullable=False, default="user")
    display_name = Column(String, nullable=False, default="user")
    password_hash = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    avatar_url = Column(
        String,
        default="https://frontend-assistain-ai-chatbot.vercel.app/Ellipse%201.svg",
    )
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_code = Column(String, nullable=True)
