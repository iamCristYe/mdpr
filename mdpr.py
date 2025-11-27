from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
import time

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def remove_all_params(url):
    parsed = urlparse(url)
    clean_url = parsed._replace(query="quality=100").geturl()
    return clean_url


# 解析HTML
def parse_html():
    headers = {
        "User-Agent": "curl/8.5.0",
    }
    photos_html = requests.get(
        "https://mdpr.jp/photo/detail/19354863", headers=headers
    ).text
    with open("photos.html", "w", encoding="utf-8") as f:
        f.write(photos_html)

    picture_url_list = []
    for img in (
        BeautifulSoup(photos_html, "lxml")
        .find_all("div", class_="pg-photo__body")[0]
        .find_all("img")
    ):
        # print(img)
        img_src = img["src"]
        if "protect" not in img_src:
            print(img_src)
            print(remove_all_params(img_src))
            picture_url_list.append(remove_all_params(img_src))

    for img in (
        BeautifulSoup(photos_html, "lxml")
        .find_all("ol", class_="pg-photo__webImageList")[0]
        .find_all("img")
    ):
        # print(img)
        img_src = img["src"]
        if "protect" not in img_src:
            print(img_src)
            print(remove_all_params(img_src))
            picture_url_list.append(remove_all_params(img_src))

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
