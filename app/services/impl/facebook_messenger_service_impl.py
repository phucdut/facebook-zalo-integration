import asyncio
import time
import traceback
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api import deps
from app.common import parameters, util
from app.common.logger import setup_logger
from app.core.config import settings
from app.crud.crud_user import crud_user
from app.schema.message_schema import MessageInDBSchema
from app.schema.user_schema import UserResponseSchema
from app.services.abc.facebook_messenger_service import FacebookMessengerService

logger = setup_logger()


class FacebookMessengerServiceImpl(FacebookMessengerService):
    def __init__(self):
        self.__crud_user = crud_user

    def get_webhook(self, request: Request) -> str:
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

    async def post_webhook(self, request: Request) -> str:
        try:
            body = await request.json()
            if body.get("object") == "page":
                for entry in body.get("entry", []):
                    messaging = entry.get("messaging", [])

                    if len(messaging) == 0:
                        continue

                    webhook_event = messaging[0]
                    # print(f"Webhook event received: {webhook_event}")

                    sender_psid = webhook_event.get("sender", {}).get("id")
                    if sender_psid:
                        # print("Sender PSID:", sender_psid)

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


# async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
#     user_info = await get_user_info(sender_psid)
#     # message = received_message.get("text")

#     # messages = dict()

#     # messages.update(
#     #     {
#     #         "store_id": "bd9256f4-04dc-47ce-91e8-1a51d36cac8a",
#     #         "customer_id": "bd9256f4-04dc-47ce-91e8-1a51d36cac8a",
#     #         "message": message,
#     #     }
#     # )

#     # send_message_url = f"{settings.AI_URL}/agent/chat/"

#     # logger.info(f"Send Message URL: {send_message_url}")

#     # async with httpx.AsyncClient() as client:
#     #     response = await client.post(send_message_url, json=messages)

#     # response_text = response.json().get("response")
#     # # response_json = response.json()

#     # print(f"Response Text: {response_text}")

#     print(f"User Info: {user_info}")

#     if user_info:
#         first_name = user_info.get("first_name", "")
#         last_name = user_info.get("last_name", "")
#         full_name = f"{first_name} {last_name}".strip()

#         response_text = (
#             f"{full_name}, bạn đã gửi tin nhắn: "
#             + received_message.get("text", "")
#         )
#     else:
#         response_text = "Đã nhận tin nhắn: " + received_message.get("text", "")

#     await call_send_api(sender_psid, response_text)

# Dictionary để lưu tin nhắn tạm theo sender_psid
user_message_buffer = {}
# Dictionary để lưu hẹn giờ cho từng sender_psid
message_timers = {}


async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
    await send_typing_on(sender_psid)

    # Create variables to store the text message and attachment URL
    message_text = ""
    attachment_url = ""

    # Check if the received message contains text
    if "text" in received_message:
        message_text = received_message.get("text", "")

    # Check if the received message contains an attachment
    if "attachments" in received_message:
        attachment_url = received_message["attachments"][0]["payload"]["url"]

    # Combine text message and attachment URL (if both are present)
    if message_text and attachment_url:
        combined_message = f"{message_text}\nAttachment: {attachment_url}"
    elif message_text:
        combined_message = message_text
    elif attachment_url:
        combined_message = f"Attachment: {attachment_url}"
    else:
        combined_message = "Received an empty message."

    # If there's no message in the buffer yet, initialize a buffer for the user
    if sender_psid not in user_message_buffer:
        user_message_buffer[sender_psid] = []

    # Add the new message to the buffer
    user_message_buffer[sender_psid].append(combined_message)

    # Reset the timer if one already exists for the user
    if sender_psid in message_timers:
        message_timers[sender_psid].cancel()

    # Create a new timer for the user to send the combined message later
    message_timers[sender_psid] = asyncio.create_task(
        send_combined_message(sender_psid)
    )

    await send_typing_off(sender_psid)


# async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
#     await send_typing_on(sender_psid)

#     # Kiểm tra nếu tin nhắn nhận được có chứa văn bản
#     if "text" in received_message:
#         # Nhận tin nhắn văn bản từ người dùng
#         message = received_message.get("text", "")

#         # Nếu chưa có tin nhắn nào trong buffer, khởi tạo buffer cho người dùng
#         if sender_psid not in user_message_buffer:
#             user_message_buffer[sender_psid] = []

#         # Thêm tin nhắn mới vào buffer
#         user_message_buffer[sender_psid].append(message)

#         # Reset hẹn giờ nếu đã có
#         if sender_psid in message_timers:
#             message_timers[sender_psid].cancel()

#         # Tạo hẹn giờ mới cho người dùng
#         message_timers[sender_psid] = asyncio.create_task(
#             send_combined_message(sender_psid)
#         )

#         await send_typing_off(sender_psid)

#     # Kiểm tra nếu tin nhắn nhận được có chứa tệp đính kèm
#     elif "attachments" in received_message:
#         attachment_url = received_message["attachments"][0]["payload"]["url"]
#         # messages.update(
#         #     {
#         #         "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
#         #         "customer_id": sender_psid,
#         #         "message": attachment_url,
#         #     }
#         # )
#         # logger.info(f"Attachment URL: {attachment_url}")

#         # Tạo payload cho phản hồi với hình ảnh và nút
#         response_payload = {
#             "attachment": {
#                 "type": "template",
#                 "payload": {
#                     "template_type": "generic",
#                     "elements": [
#                         {
#                             "title": "Đây có phải là bức ảnh đúng không?",
#                             "subtitle": "Nhấn một nút để trả lời.",
#                             "image_url": attachment_url,
#                             "buttons": [
#                                 {
#                                     "type": "postback",
#                                     "title": "Có!",
#                                     "payload": "yes",
#                                 },
#                                 {
#                                     "type": "postback",
#                                     "title": "Không!",
#                                     "payload": "no",
#                                 },
#                             ],
#                         }
#                     ],
#                 },
#             }
#         }

#         # Gọi API để gửi phản hồi với hình ảnh và các nút
#         await call_send_api(sender_psid, response_payload)

#         await send_typing_off(sender_psid)
#         return  # Kết thúc sớm sau khi gửi phản hồi

#     else:
#         response_text = "Nhận được một tin nhắn trống."
#         await call_send_api(sender_psid, {"text": response_text})


async def send_combined_message(sender_psid: str):
    # Chờ 10 giây
    await asyncio.sleep(10)

    # Gộp tất cả các tin nhắn thành 1 chuỗi
    combined_message = " ".join(user_message_buffer[sender_psid])

    # Gửi tin nhắn gộp lên backend
    messages = {
        "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
        "customer_id": sender_psid,
        "message": combined_message,
    }

    logger.info(f"Tin nhắn đã gộp để gửi lên API: {messages}")

    send_message_url = f"{settings.AI_URL}/agent/chat/"

    # Gọi API gửi tin nhắn
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                send_message_url, json=messages, timeout=10
            )
            logger.info(
                f"Phản hồi từ API: {response.status_code}, {response.text}"
            )

            if response.status_code == 200:
                response_json = response.json()
                response_text = response_json.get(
                    "response", "Không có phản hồi từ API."
                )
            else:
                response_text = "API gặp sự cố. Vui lòng thử lại sau."

        except Exception as e:
            logger.error(f"Lỗi xảy ra khi gọi API: {str(e)}")
            response_text = "Đã xảy ra lỗi khi gọi API. Vui lòng thử lại sau."

    # Gửi phản hồi về người dùng
    await call_send_api(sender_psid, {"text": response_text})

    # Xóa buffer và hẹn giờ sau khi đã gửi tin nhắn lên BE
    del user_message_buffer[sender_psid]
    if sender_psid in message_timers:
        message_timers[sender_psid].cancel()
        del message_timers[sender_psid]


# async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
#     await send_typing_on(sender_psid)

#     user_info = await get_user_info(sender_psid)
#     message = received_message.get("text")

#     logger.info(f"Received Message: {received_message}")

#     text = """Chào chị, em rất vui khi được trò chuyện với chị! Hôm nay em muốn giới thiệu đến chị một số sản phẩm đang được ưa chuộng nhất hiện nay."""

#     messages = {
#         "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
#         "customer_id": "bd9256f4-04dc-47ce-91e8-1a51d36cac8a",
#         "message": message,
#     }

#     logger.info(f"Messages being sent to API: {messages}")

#     send_message_url = f"{settings.AI_URL}/agent/chat/"

#     # Kiểm tra nếu tin nhắn nhận được có chứa văn bản
#     if "text" in received_message:
#         async with httpx.AsyncClient() as client:
#             try:
#                 response = await client.post(
#                     send_message_url, json=messages, timeout=10
#                 )
#                 logger.info(f"API Response Status: {response.status_code}")
#                 logger.info(f"API Response Text: {response.text}")

#                 if response.status_code == 200:
#                     response_json = response.json()
#                     response_text = response_json.get(
#                         "response", "Không có phản hồi từ API."
#                     )
#                     logger.info(f"Response Text: {response_text}")
#                 else:
#                     response_text = "API gặp sự cố. Vui lòng thử lại sau."
#                     logger.error(
#                         f"API call failed with status code {response.status_code} and response: {response.text}"
#                     )

#             except Exception as e:
#                 logger.error(f"Exception occurred during API call: {str(e)}")
#                 logger.error(
#                     traceback.format_exc()
#                 )  # Thêm traceback để ghi lại thông tin lỗi đầy đủ
#                 response_text = (
#                     "Đã xảy ra lỗi khi gọi API. Vui lòng thử lại sau."
#                 )

#         # Gọi API để gửi phản hồi văn bản trở lại cho người dùng
#         await call_send_api(sender_psid, {"text": response_text})

#     # Kiểm tra nếu tin nhắn nhận được có chứa tệp đính kèm
#     elif "attachments" in received_message:
#         attachment_url = received_message["attachments"][0]["payload"]["url"]
#         messages.update(
#             {
#                 "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
#                 "customer_id": sender_psid,
#                 "message": attachment_url,
#             }
#         )
#         logger.info(f"Attachment URL: {attachment_url}")

#         # Tạo payload cho phản hồi với hình ảnh và nút
#         response_payload = {
#             "attachment": {
#                 "type": "template",
#                 "payload": {
#                     "template_type": "generic",
#                     "elements": [
#                         {
#                             "title": "Đây có phải là bức ảnh đúng không?",
#                             "subtitle": "Nhấn một nút để trả lời.",
#                             "image_url": attachment_url,
#                             "buttons": [
#                                 {
#                                     "type": "postback",
#                                     "title": "Có!",
#                                     "payload": "yes",
#                                 },
#                                 {
#                                     "type": "postback",
#                                     "title": "Không!",
#                                     "payload": "no",
#                                 },
#                             ],
#                         }
#                     ],
#                 },
#             }
#         }

#         # Gọi API để gửi phản hồi với hình ảnh và các nút
#         await call_send_api(sender_psid, response_payload)

#         await send_typing_off(sender_psid)
#         return  # Kết thúc sớm sau khi gửi phản hồi

#     else:
#         response_text = "Nhận được một tin nhắn trống."
#         await call_send_api(sender_psid, {"text": response_text})


# async def handle_message(sender_psid: str, received_message: Dict[str, Any]):
#     user_info = await get_user_info(sender_psid)
#     message = received_message.get("text")

#     logger.info(f"Received Message: {received_message}")

#     text = """Chào chị, em rất vui khi được trò chuyện với chị! Hôm nay em muốn giới thiệu đến chị một số sản phẩm đang được ưa chuộng nhất hiện nay."""

#     messages = dict()

#     messages.update(
#         {
#             "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
#             "customer_id": "bd9256f4-04dc-47ce-91e8-1a51d36cac8a",
#             "message": message,
#         }
#     )

#     send_message_url = f"{settings.AI_URL}/agent/chat/"

#     # Kiểm tra nếu tin nhắn nhận được có chứa văn bản
#     if "text" in received_message:
#         print("Text message received")
#         # async with httpx.AsyncClient() as client:
#         #     response = await client.post(send_message_url, json=messages)

#         #     response_json = response.json()
#         #     response_text = response_json.get(
#         #         "response", "Không có phản hồi từ API."
#         #     )
#         #     logger.info(f"Response Text: {response_text}")

#     # Kiểm tra nếu tin nhắn nhận được có chứa tệp đính kèm
#     elif "attachments" in received_message:
#         attachment_url = received_message["attachments"][0]["payload"]["url"]
#         messages.update(
#             {
#                 "store_id": "a23a71d3-9647-4b8e-bd48-fe9c8f776130",
#                 "customer_id": sender_psid,
#                 "message": attachment_url,
#             }
#         )
#         # async with httpx.AsyncClient() as client:
#         #     response = await client.post(send_message_url, json=messages)

#         # response_text = response.json().get("response")

#         # Tạo payload cho phản hồi với hình ảnh và nút
#         response_payload = {
#             "attachment": {
#                 "type": "template",
#                 "payload": {
#                     "template_type": "generic",
#                     "elements": [
#                         {
#                             "title": "Đây có phải là bức ảnh đúng không?",
#                             "subtitle": "Nhấn một nút để trả lời.",
#                             "image_url": attachment_url,
#                             "buttons": [
#                                 {
#                                     "type": "postback",
#                                     "title": "Có!",
#                                     "payload": "yes",
#                                 },
#                                 {
#                                     "type": "postback",
#                                     "title": "Không!",
#                                     "payload": "no",
#                                 },
#                             ],
#                         }
#                     ],
#                 },
#             }
#         }

#         # Gọi API để gửi phản hồi với hình ảnh và các nút
#         await call_send_api(sender_psid, response_payload)
#         return  # Kết thúc sớm sau khi gửi phản hồi

#     else:
#         response_text = "Nhận được một tin nhắn trống."

#     # Gọi API để gửi phản hồi văn bản trở lại cho người dùng
#     await call_send_api(sender_psid, {"text": text})


async def handle_postback(sender_psid: str, received_postback: Dict[str, Any]):
    # Implement logic to handle postback events
    payload = received_postback.get("payload")
    response_text: str

    # Set the response based on the postback payload
    if payload == "yes":
        response_text = "Cảm ơn bạn!"  # "Thanks!" in Vietnamese
    elif payload == "no":
        response_text = "Rất tiếc, hãy thử gửi một hình ảnh khác."  # "Oops, try sending another image." in Vietnamese
    else:
        response_text = "Xin lỗi, tôi không hiểu yêu cầu của bạn."  # Generic fallback message

    # Send the response back to the user
    await call_send_api(sender_psid, {"text": response_text})


async def send_typing_on(sender_psid: str):
    typing_on_payload = {
        "recipient": {"id": sender_psid},
        "sender_action": "typing_on",
    }
    await call_send_api(sender_psid, typing_on_payload)


async def send_typing_off(sender_psid: str):
    typing_off_payload = {
        "recipient": {"id": sender_psid},
        "sender_action": "typing_off",
    }
    await call_send_api(sender_psid, typing_off_payload)


async def send_typing_action(sender_psid: str, action: str = "typing_on"):
    """
    Send typing action to the user. Can be 'typing_on', 'typing_off', or 'mark_seen'.
    """
    send_api_url = f"{settings.FACEBOOK_URL}/v11.0/me/messages?access_token={settings.PAGE_ACCESS_TOKEN}"

    action_payload = {
        "recipient": {"id": sender_psid},
        "sender_action": action,
    }

    async with httpx.AsyncClient() as client:
        await client.post(send_api_url, json=action_payload)


# async def call_send_api(sender_psid: str, response: Union[str, Dict[str, Any]]):
#     send_api_url = f"{settings.FACEBOOK_URL}/v11.0/me/messages?access_token={settings.PAGE_ACCESS_TOKEN}"

#     # Build the payload based on the response type
#     if isinstance(response, str):
#         payload = {
#             "recipient": {"id": sender_psid},
#             "message": {"text": response},
#         }
#     else:
#         payload = {"recipient": {"id": sender_psid}, "message": response}

#     headers = {"Content-Type": "application/json"}

#     # Send the request to Facebook's Send API
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(
#                 send_api_url, json=payload, headers=headers
#             )
#             response.raise_for_status()  # Raise an exception for any HTTP errors
#             logger.info(f"Message sent to {sender_psid}")
#         except httpx.HTTPStatusError as e:
#             logger.error(
#                 f"Error sending message: {e.response.status_code} - {e.response.text}"
#             )
#         except Exception as e:
#             logger.error(f"An unexpected error occurred: {str(e)}")


async def call_send_api(sender_psid: str, response: Union[str, Dict[str, Any]]):
    send_api_url = f"{settings.FACEBOOK_URL}/v11.0/me/messages?access_token={settings.PAGE_ACCESS_TOKEN}"

    # Gửi hành động "typing_on" trước khi xử lý tin nhắn
    await send_typing_action(sender_psid, "typing_on")

    # Chờ một khoảng thời gian ngắn để mô phỏng quá trình xử lý (tùy chọn)
    await asyncio.sleep(2)  # Chờ 2 giây cho hiệu ứng typing

    # Xây dựng payload dựa trên kiểu phản hồi
    if isinstance(response, str):
        message_payload = {
            "recipient": {"id": sender_psid},
            "message": {"text": response},
        }
    else:
        message_payload = {
            "recipient": {"id": sender_psid},
            "message": response,
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(send_api_url, json=message_payload)
            logger.info(f"Sent message: {message_payload} to {sender_psid}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

    # Sau khi xử lý xong, gửi hành động "typing_off"
    await send_typing_action(sender_psid, "typing_off")


async def get_user_info(sender_psid: str):
    url = f"{settings.FACEBOOK_URL}/v11.0/{sender_psid}?fields=first_name,last_name,profile_pic&access_token={settings.PAGE_ACCESS_TOKEN}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            user_info = response.json()
            print(f"User Info: {user_info}")
            return user_info
        else:
            print(f"Error fetching user info: {response.text}")
            return None
