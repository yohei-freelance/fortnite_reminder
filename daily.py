from linebot import LineBotApi
from linebot.models import (
    TextSendMessage
)

import pandas as pd
import numpy as np
import os
from datetime import datetime, timezone, timedelta
from csv import DictWriter
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("function_num")
args = parser.parse_args()

channel_access_token = os.getenv("LINEBOT_ACCESS_TOKEN")
line_bot_api = LineBotApi(channel_access_token)

userinfo_path = "/home/ec2-user/data/user.csv"
df_user = pd.read_csv(userinfo_path)
JST = timezone(timedelta(hours=+9), 'JST')
d_today = datetime.now(JST).date()
todaytable_name = f"record_{d_today}"
todaytable_path = "/home/ec2-user/record/" + todaytable_name + ".csv"

def initialize_table():
    df_today = pd.DataFrame([
        [user_id, "未登録"] for user_id in df_user.userId.values],
        columns=["userId", "join_or_not"])
    df_today.to_csv(todaytable_path, index=False)
    print("successfully initialized tables.")
    return

def broadcast_morning():
    line_bot_api.broadcast(TextSendMessage(text="今日も元気に頑張りましょう！一日終わりのゲームはどうですか？？"))
    return

def broadcast_evening():
    to = []
    df_today = pd.read_csv(todaytable_path)
    for index, row in df_today.iterrows():
        if row["join_or_not"] == "未登録":
            to.append(row["userId"])
    line_bot_api.multicast(to, TextSendMessage(text="まだ回答をいただけてません。ぜひ登録をお願いします！"))
    return

def finalize_table():
    count_join = 0
    status = "本日は開催されます！メンバーは\n"
    df_status = pd.read_csv(todaytable_path)
    df_concat = pd.merge(df_user, df_status, on="userId")
    for index, row in df_concat.iterrows():
        user_name = row["userName"]
        join_or_not = row["join_or_not"]
        if join_or_not == "未登録":
            join_or_not = "不参加"
        if join_or_not == "参加":
            count_join += 1
            status += f"{user_name} "
        status += "です。"
    if count_join >= 2:
        status += "\n本日は開催可能です。"
        line_bot_api.broadcast(TextSendMessage(text=status))
    return

if __name__ == '__main__':
    # 毎日0時1分
    if args.function_num == "1":
        initialize_table()
    # 毎日8時
    elif args.function_num == "2":
        broadcast_morning()
    # 毎日16時
    elif args.function_num == "3":
        broadcast_evening()
    # 毎日17時
    elif args.function_num == "4":
        finalize_table()
