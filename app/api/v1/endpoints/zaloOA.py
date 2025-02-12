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

router = APIRouter()
# facebook_service = FacebookMessengerService()


@router.get("/webhook")
async def get_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == settings.MY_VERIFY_TOKEN:
            return PlainTextResponse(challenge)
        else:
            raise HTTPException(status_code=403, detail="Forbidden")
    else:
        raise HTTPException(status_code=404, detail="Not Found")


@router.post("/webhook")
async def post_webhook(request: Request):
    try:
        body = await request.json()

        if body.get("object") == "page":
            for entry in body.get("entry", []):
                messaging = entry.get("messaging", [])

                if len(messaging) == 0:
                    continue

                webhook_event = messaging[0]
                print(f"Webhook event received: {webhook_event}")

                sender_psid = webhook_event.get("sender", {}).get("id")
                if sender_psid:
                    print("Sender PSID:", sender_psid)

                    if "message" in webhook_event:
                        await handle_message(
                            sender_psid, webhook_event["message"]
                        )
                    elif "postback" in webhook_event:
                        await handle_postback(
                            sender_psid, webhook_event["postback"]
                        )

            return JSONResponse(
                content={"status": "EVENT_RECEIVED"}, status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "Invalid request"}, status_code=400
            )
    except Exception as e:
        print(f"Error handling the webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
    user_info = await get_user_info(sender_psid)

    print(f"User Info: {user_info}")

    if user_info:
        first_name = user_info.get("first_name", "")
        last_name = user_info.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()

        response_text = (
            f"{full_name}, bạn đã gửi tin nhắn: "
            + received_message.get("text", "")
        )
    else:
        response_text = "Đã nhận tin nhắn: " + received_message.get("text", "")

    await call_send_api(sender_psid, response_text)


async def handle_postback(sender_psid: str, received_postback: Dict[str, Any]):
    # Implement logic to handle postback events
    payload = received_postback.get("payload")
    response_text = f"Postback received with payload: {payload}"
    await call_send_api(sender_psid, response_text)


async def call_send_api(sender_psid: str, response: Union[str, Dict[str, Any]]):
    # Implement logic to send response messages via the Send API
    # You can use an HTTP client like `httpx` or `aiohttp` to send a POST request to the Messenger API
    send_api_url = f"https://graph.facebook.com/v11.0/me/messages?access_token={settings.PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": sender_psid},
        "message": (
            {"text": response} if isinstance(response, str) else response
        ),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(send_api_url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send message: {response.text}")


async def get_user_info(sender_psid: str):
    url = f"https://graph.facebook.com/v11.0/{sender_psid}?access_token={settings.PAGE_ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            user_info = response.json()
            print(f"User Info: {user_info}")
            return user_info
        else:
            print(f"Error fetching user info: {response.text}")
            return None
