import uuid
from typing import List, Optional

from pydantic import BaseModel

from app.schema._soft_delete_schema import SoftDeleteSchema


class MessageBaseSchema(BaseModel):
    conversation_id: uuid.UUID
    org_id: uuid.UUID
    sender_id: str
    sender_type: str
    latency: Optional[float] = None
    message: str


class MessageCreateSchema(MessageBaseSchema):
    pass


class MessageUpdateSchema(BaseModel):
    message: Optional[str] = None


class MessageInDBSchema(MessageBaseSchema, SoftDeleteSchema):
    id: uuid.UUID

    class Config:
        orm_mode = True


class MessageResponseSchema(MessageInDBSchema):
    pass


class MessageCollectionResponseSchema(BaseModel):
    messages: List[MessageInDBSchema]
