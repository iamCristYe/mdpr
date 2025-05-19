from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
import time

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
        "https://mdpr.jp/photo/detail/18432359", headers=headers
    ).text
    with open("photos.html", "w", encoding="utf-8") as f:
        f.write(photos_html)
    # print(members_html)
    # class has to be exactly the same!

    soup = BeautifulSoup(photos_html, "lxml").find_all(
        "ol", class_="pg-photo__webImageList"
    )[0]
    # print(soup)
    pics = []
    for img in soup.find_all("img"):
        # print(img)
        img_src = img["src"]
        if "protect" not in img_src:
            pics.append(remove_all_params(img_src)+"?width=38400&auto=png&quality=100")
            # replace all param of original image

            #?width=1920&auto=png&quality=100
    print(pics)
    return pics




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

            file_link = [file_link]
            response = requests.post(url, data=payload)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass



pics = parse_html()
import datetime

for i in range(len(pics)):
    pics = pics[i]

    send_telegram_file_link(
        f"{i+1}/{len(pics)}",
        pics[i],
    )
