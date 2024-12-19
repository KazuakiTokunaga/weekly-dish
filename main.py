import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from lib.recipe import get_todays_dish, get_weekly_dish

app = FastAPI()

load_dotenv()

# LINEチャネルアクセストークンとシークレット
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# LINE Messaging APIのヘッダー
HEADERS = {
    "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


@app.post("/webhook")
async def webhook(request: Request):
    """LINEからのWebhookリクエストを処理"""
    try:
        body = await request.json()

        for event in body.get("events", []):
            print(f"Received event: {event}")
            event_type = event["type"]

            # フォローイベントの処理
            if event_type == "follow":
                user_id = event["source"]["userId"]
                send_persistent_menu(user_id)

            # メッセージイベントの処理
            elif event_type == "message" and event["message"]["type"] == "text":
                user_id = event["source"]["userId"]
                user_message = event["message"]["text"]

                if user_message == "1週間分の主菜リスト":
                    _, display_string = get_weekly_dish()
                    send_reply_message(event["replyToken"], display_string)
                elif user_message == "今日の主菜候補3つ":
                    _, display_string = get_todays_dish()
                    send_reply_message(event["replyToken"], display_string)

                # 再度ボタンを表示
                send_persistent_menu(user_id)

        return {"message": "OK"}

    except Exception as e:
        # エラーが発生しても200を返す
        print(f"Error processing webhook: {e}")
        return {"message": "Error"}, 200


def send_persistent_menu(user_id: str):
    """ボタンを下部に表示し続けるメッセージを送信"""
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": "下部のボタンから選択してください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "1週間分の主菜リスト",
                                "text": "1週間分の主菜リスト",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "今日の主菜候補3つ",
                                "text": "今日の主菜候補3つ",
                            },
                        },
                    ]
                },
            }
        ],
    }

    # LINE Messaging APIにリクエストを送信
    response = requests.post("https://api.line.me/v2/bot/message/push", headers=HEADERS, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())


def send_reply_message(reply_token: str, message: str):
    """シンプルな返信メッセージを送信"""
    print(message)

    data = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": message,
            }
        ],
    }

    # LINE Messaging APIにリクエストを送信
    response = requests.post("https://api.line.me/v2/bot/message/reply", headers=HEADERS, json=data)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())


@app.get("/")
async def root():
    return {"message": "LINE Chatbot with FastAPI is running!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="debug")
