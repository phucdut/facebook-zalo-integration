from sqlalchemy import Column, String

from app.db.base_class import Base


class Item(Base):
    full_name = Column(String)
