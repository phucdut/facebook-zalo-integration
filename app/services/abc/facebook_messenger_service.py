from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from fastapi import Request
from sqlalchemy.orm import Session

from app.schema.user_schema import UserResponseSchema


class FacebookMessengerService(ABC):
    @abstractmethod
    def get_webhook(
        self,
        request: Request,
    ) -> str:
        pass

    @abstractmethod
    async def post_webhook(
        self,
        request: Request,
    ) -> str:
        pass
