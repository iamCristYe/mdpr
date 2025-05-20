import os
import time
import requests

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


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


def get_send(id):
    consecutive_not_found = 0
    for i in range(9999):
        if consecutive_not_found >= 5:
            print("No more images found, stopping.")
            print("Finished sending images.")
            break
        url = f"https://lemino.docomo.ne.jp/ft/{id}/images/cntents_{i}.webp"
        response = requests.head(url)
        if response.status_code == 200:
            print(f"Image URL: {url}")
            send_telegram_photo(f"Image URL: {url}", url)
        else:
            print(f"No images found for {url}")
            consecutive_not_found += 1
        time.sleep(5)


get_send("0000013")
get_send("0000045")
get_send("0000046")
