# This Python file uses the following encoding: utf-8

from typing import Union, List, Dict
import os

from fastapi import FastAPI, Request
import uvicorn
from linebot import WebhookParser, LineBotApi
from aiolinebot import AioLineBotApi
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, PostbackAction, URIAction
)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from csv import DictWriter

app = FastAPI()

# Linebot variables definition
channel_access_token = os.environ.get("LINEBOT_ACCESS_TOKEN")
channel_secret = os.environ.get("LINEBOT_SECRET")
line_bot_api_aio = AioLineBotApi(channel_access_token)
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

# Table definition
userinfo_path = "/home/ec2-user/data/user.csv"
df_user = pd.read_csv(userinfo_path)
log_path = "/home/ec2-user/log/historical.csv"
df_historical = pd.read_csv(userinfo_path)
headerCSV_user = ["userId", "userName"]
headerCSV_historical = ["userId", "text", "time"]

JST = timezone(timedelta(hours=+9), 'JST')
d_today = datetime.now(JST).date()
todaydata_path = f"/home/ec2-user/record/record_{d_today}.csv"

@app.get('/')
def read_main():
    return { "state" : "This server runs well."}

@app.get('/requests')
def read_requests():
    return { "requests" : "probably comming soon"}

def reply_message_async(reply_token: str, reply_text: Union[List, str]):
    if type(reply_text) == str:
        return line_bot_api_aio.reply_message_async(
            reply_token,
            TextMessage(text=f"{reply_text}")
            )
    else:
        reply_texts = []
        for text in reply_text:
            reply_texts.append(TextSendMessage(text=text))
        return line_bot_api_aio.reply_message_async(
            reply_token,
            reply_texts
            )

def append_csv(csv_path: str, headers: List, append_dict: Dict):
    with open(f"{csv_path}", 'a', newline='') as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=headers)
        dictwriter_object.writerow(append_dict)
        f_object.close()
    return

def read_text_and_reply(reply_token: str, text_path: str):
    f = open(text_path, 'r', encoding='UTF-8')
    text = f.read()
    return reply_message_async(reply_token, text)

@app.post("/messaging_api/handle_request")
async def handle_request(request: Request):
    events = parser.parse(
        (await request.body()).decode("utf-8"),
        request.headers.get("X-Line-Signature", ""))
    # datetime
    JST = timezone(timedelta(hours=+9), 'JST')
    d_today = datetime.now(JST).date()
    todaydata_path = f"/home/ec2-user/record/record_{d_today}.csv"
    # dispose of each events
    for ev in events:
        user_id = ev.source.user_id
        df_user = pd.read_csv(userinfo_path)
        # for the first access: user registration
        if ev.type == "follow":
            df_user = pd.read_csv(userinfo_path)
            user_name = line_bot_api.get_profile(user_id).display_name
            if user_id not in df_user.userId.values:
                data_to_append = {"userId": f"{user_id}", "userName": f"{user_name}"}
                append_csv(csv_path=userinfo_path, headers=headerCSV_user, append_dict=data_to_append)
            await reply_message_async(ev.reply_token, [f"はじめまして{user_name}さん！ \n私はGamewithそぞくのネフライトです！", "このbotは毎日朝の8時から夕方の17時までに皆さんの予定を集計して、ぼく>が大好きなfortniteを効率的に楽しんでもらうためのものです！", "使い方で不明な点があったり、さらにアドバンスドな使い方をしたい場合はhelpと入力してくださいね!"])
        elif ev.type == "message":
            present_time = datetime.now(JST)
            content = ev.message.text
            data_to_append={"userId": f"{user_id}", "text": content, "time": f"{present_time}"}
            append_csv(csv_path=log_path, headers=headerCSV_historical, append_dict=data_to_append)
            if content == "参加します":
                df_record = pd.read_csv(todaydata_path, index_col=0)
                current_status = df_record.loc[user_id, "join_or_not"]
                if current_status == "参加":
                    await reply_message_async(reply_token=ev.reply_token, reply_text="既に「参加」として登録されています。")
                else:
                    if current_status == "未登録":
                        user_name = line_bot_api.get_profile(user_id).display_name
                        line_bot_api.broadcast(TextSendMessage(text=f"{user_name}さんが参加表明しました！"))
                    df_record.at[user_id, "join_or_not"] = "参加"
                    df_record.to_csv(todaydata_path, index=True)
                    await reply_message_async(reply_token=ev.reply_token, reply_text=f"「{current_status}」から「参加」に変更しました。楽しみましょう！")
            elif content == "参加しません":
                df_record = pd.read_csv(todaydata_path, index_col=0)
                current_status = df_record.loc[user_id, "join_or_not"]
                if current_status == "不参加":
                    await reply_message_async(reply_token=ev.reply_token, reply_text="既に「不参加」として登録されています。")
                else:
                    df_record.at[user_id, "join_or_not"] = "不参加"
                    df_record.to_csv(todaydata_path, index=True)
                    await reply_message_async(reply_token=ev.reply_token, reply_text=f"「{current_status}」から「不参加」に変更しました。素敵な自由時間をお過ごしください！")
            elif content == "ヘルプ":
                await read_text_and_reply(reply_token=ev.reply_token, text_path='documents/function.txt')
            elif content == "アプデ予定":
                await read_text_and_reply(reply_token=ev.reply_token, text_path='documents/update.txt')
            elif content == "ステータス":
                status = ""
                df_status = pd.read_csv(todaydata_path)
                df_concat = pd.merge(df_user, df_status, on="userId")
                for index, row in df_concat.iterrows():
                    user_name = row["userName"]
                    join_or_not = row["join_or_not"]
                    status += f"{user_name}さんは「{join_or_not}」です。"
                await reply_message_async(reply_token=ev.reply_token, reply_text=status)
            await reply_message_async(reply_token=ev.reply_token, reply_text="メッセージありがとうございます。いただいたメッセージには現在非対応です。")
        elif ev.type == "unfollow":
            pass
        else:
            await reply_message_async(
                reply_token=ev.reply_token,
                reply_text="開発者はまだlinebotに詳しくないため、その挙動への対応を考えていません。ごめん。"
            )

    # LINEサーバへHTTP応答を返す
    return "ok"
