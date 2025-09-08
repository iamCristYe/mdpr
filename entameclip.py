from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
import time
import re

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def remove_all_params(url):
    parsed = urlparse(url)
    clean_url = parsed._replace(query="").geturl()
    return clean_url


# 解析HTML
def parse_html():
    headers = {
        "User-Agent": "curl/8.5.0",
    }
    photos_html = requests.get(
        "https://entameclip.com/picture/453042/", headers=headers
    ).text
    with open("photos.html", "w", encoding="utf-8") as f:
        f.write(photos_html)

    picture_url_list = []
    for img in (
        BeautifulSoup(photos_html, "lxml").find_all("figure")
         
    ):
        print(img)
        img_src = img.find_all("img")[0]["srcset"]
        picture_url_list.append(img_src.split(",")[-1].split(" ")[1].split("-")[0]+".webp")

    print(picture_url_list)
    print(len(picture_url_list))
    return picture_url_list


def send_telegram_photo(caption, img_url):
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": img_url,
                "caption": caption,
            }

            response = requests.post(url, json=payload)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass


def send_telegram_file_link(caption, file_link):
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"

            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "document": file_link,
                "parse_mode": "HTML",
            }

            response = requests.post(url, data=payload)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
            else:
                print(response_body)
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass


picture_url_list = parse_html()
import datetime

for i in range(len(picture_url_list)):
    picture_url = picture_url_list[i]

    send_telegram_file_link(
        f"{i+1}/{len(picture_url_list)}",
        picture_url,
    )
