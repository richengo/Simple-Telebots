# -*- coding: utf-8 -*-
"""
This is a simple telegram bot to create a to-do list
Reference: Gareth Dwyer
@author: Riche
"""

import json
import requests
import time
import urllib
from dbhelper import DBHelper

TOKEN = "<your-bot-token>"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

db = DBHelper()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    # timeout is long polling technique so that telegram keeps connection until there are updates
    url = URL + "getUpdates?timeout=100"
    # offset tells the API that we dont want prev msgs
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js

# Function that calculates the highest ID of all the updates we receive from get_updates
def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id, reply_markup=None):
    # urllib helps to handle special characters
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    # to include custom keyboard
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

# Function to present a custom Telegram keyboard
def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)

# Function to handle updates
def handle_updates(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)
            if text == "/done":
                keyboard = build_keyboard(items)
                send_message("Select an item to delete", chat, keyboard)
            # Sends a welcome msg
            elif text == "/start":
                send_message("Welcome to you personal To Do list. Send any text to me and I'll store it as an item. Send /done to remove items", chat)
            elif text.startswith("/"):
                continue
            elif text in items:
                db.delete_item(text, chat)
                items = db.get_items(chat)
                keyboard = build_keyboard(items)
                send_message("Select an item to delete", chat, keyboard)
            else:
                db.add_item(text, chat)
                items = db.get_items(chat)
                message = "\n".join(items)
                send_message(message, chat)
        except KeyError:
            pass

def main():
    db.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)
        time.sleep(0.5)

# Code will execute every 0.5s
if __name__ == '__main__':
    main()
