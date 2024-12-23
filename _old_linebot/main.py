import os
from collections import defaultdict

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

from lib.ingredients import get_ingredients_for_menus
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

# ユーザーごとの一時状態管理
user_states = defaultdict(dict)


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

                if user_message in ["1週間分の主菜リスト", "別の主菜リスト"]:
                    weekly_dishes, weekly_display_string = get_weekly_dish()
                    user_states[user_id]["weekly_dishes"] = weekly_dishes
                    user_states[user_id]["weekly_display"] = weekly_display_string
                    send_reply_message(event["replyToken"], weekly_display_string)

                    send_weekly_dish_options(user_id)

                elif user_message in ["今日の主菜候補3つ", "別の主菜候補3つ"]:
                    daily_dishes, daily_display_string = get_todays_dish()
                    user_states[user_id]["daily_dishes"] = daily_dishes
                    user_states[user_id]["daily_display"] = daily_display_string
                    send_reply_message(event["replyToken"], daily_display_string)

                    send_todays_dish_options(user_id)

                elif user_message in ["食材を表示"]:  # 1週間分の主菜リストのオプション
                    _, ingredients_string = get_ingredients_for_menus(user_states[user_id]["weekly_dishes"])
                    send_reply_message(event["replyToken"], ingredients_string)

                    send_persistent_menu(user_id)

                elif user_message in ["1の食材", "2の食材", "3の食材"]:
                    daily_dishes = user_states[user_id]["daily_dishes"]
                    target = int(user_message[0]) - 1
                    dish = daily_dishes[target]
                    ingredients, ingredients_string = get_ingredients_for_menus([dish])
                    send_reply_message(event["replyToken"], ingredients_string)

                    send_persistent_menu(user_id)

                else:
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


def send_weekly_dish_options(user_id: str):
    """1週間分の主菜リストの選択後のオプションを表示"""
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": "オプションを選択してください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "食材を表示",
                                "text": "食材を表示",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "別の主菜リスト",
                                "text": "別の主菜リスト",
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


def send_todays_dish_options(user_id: str):
    """今日の主菜候補3つの選択後のオプションを表示"""
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": "オプションを選択してください",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "1の食材",
                                "text": "1の食材",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "2の食材",
                                "text": "2の食材",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "3の食材",
                                "text": "3の食材",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "別の主菜候補3つ",
                                "text": "別の主菜候補3つ",
                            },
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "message",
                                "label": "1週間分の主菜リスト",
                                "text": "1週間分の主菜リスト",
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
