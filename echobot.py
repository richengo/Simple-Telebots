# -*- coding: utf-8 -*-
"""
This is a simple telegram bot to echo the text input of users
Reference: Gareth Dwyer
@author: Riche
"""

import json
import requests
import time
import urllib

TOKEN = "<your-bot-token>"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


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

# Function to send an echo reply for each message we receive
def echo_all(updates):
    for update in updates["result"]:
        try:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            send_message(text, chat)
        except Exception as e:
            print(e)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    # urllib helps to handle special characters
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)

# Code will execute every 0.5s
if __name__ == '__main__':
    main()
