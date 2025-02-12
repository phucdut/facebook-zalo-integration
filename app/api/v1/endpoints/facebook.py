import os
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.common import parameters
from app.core.config import settings
from app.schema.user_schema import UserResponseSchema
from app.services.impl.facebook_messenger_service_impl import (
    FacebookMessengerServiceImpl,
)

router = APIRouter()
facebook_messenger_service = FacebookMessengerServiceImpl()


@router.get("/webhook")
def get_webhook(
    request: Request,
):
    return facebook_messenger_service.get_webhook(
        request=request,
    )


@router.post("/webhook")
async def post_webhook(
    request: Request,
):
    return await facebook_messenger_service.post_webhook(
        request=request,
    )
