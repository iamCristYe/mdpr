from bs4 import BeautifulSoup
import requests
import os
import time
import re
from urllib.parse import urljoin

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_THREAD_ID = os.environ.get("TELEGRAM_THREAD_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# New: configure which ORICON news/gallery to scrape
ORICON_NEWS_ID = os.environ.get("ORICON_NEWS_ID", "2443390")  # example
ORICON_START_INDEX = int(os.environ.get("ORICON_START_INDEX", "1"))

# ---------- Telegram senders (reuse your existing ones) ----------

def send_telegram_photo(caption, img_url):
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "photo": img_url,
                "caption": caption,
            }
            if TELEGRAM_THREAD_ID is not None:
                payload["message_thread_id"] = TELEGRAM_THREAD_ID
            response = requests.post(url, json=payload, timeout=30)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
            else:
                # print for debugging
                print("sendPhoto error:", response_body)
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
            if TELEGRAM_THREAD_ID is not None:
                payload["message_thread_id"] = TELEGRAM_THREAD_ID
            response = requests.post(url, data=payload, timeout=60)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
            else:
                print("sendDocument link error:", response_body)
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass

def send_telegram_message(caption):
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": caption,
                "parse_mode": "HTML",
            }
            if TELEGRAM_THREAD_ID is not None:
                payload["message_thread_id"] = TELEGRAM_THREAD_ID
            response = requests.post(url, data=payload, timeout=30)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
            else:
                print("sendMessage error:", response_body)
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass

# ---------- Optional: Upload file if hotlinking is blocked ----------
def send_telegram_file_upload(caption, img_url):
    """
    Fallback: download image bytes then upload to Telegram as a document.
    Use this if direct URL sending fails due to anti-hotlinking.
    """
    while True:
        try:
            # Download
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Referer": "https://www.oricon.co.jp/",
            }
            r = requests.get(img_url, headers=headers, timeout=60)
            r.raise_for_status()

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            files = {
                "document": ("photo.jpg", r.content, "image/jpeg")
            }
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML",
            }
            if TELEGRAM_THREAD_ID is not None:
                data["message_thread_id"] = TELEGRAM_THREAD_ID

            response = requests.post(url, data=data, files=files, timeout=120)
            response_body = response.json()
            if "error_code" not in response_body:
                time.sleep(5)
                return
            else:
                print("sendDocument upload error:", response_body)
                time.sleep(5)
                return
        except Exception as e:
            print(e)
            time.sleep(5)
            pass

# ---------- ORICON parser ----------
def parse_oricon_gallery(news_id, start_index=1, max_pages=1000, delay=0.4):
    """
    Crawl ORICON gallery, starting at /news/{news_id}/photo/{start_index}/
    Follow the 'next' arrow until it ends. Returns list of unique image URLs.
    """
    BASE = "https://www.oricon.co.jp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }

    img_pattern = re.compile(r"^https://contents\.oricon\.co\.jp/upimg/news/")
    seen = set()
    ordered_urls = []

    # Start URL
    url = f"{BASE}/news/{news_id}/photo/{start_index}/"

    for _ in range(max_pages):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code >= 400:
                # Stop on 404 or other errors
                print(f"Stop: HTTP {resp.status_code} at {url}")
                break

            soup = BeautifulSoup(resp.text, "lxml")

            # Strategy 1: find the main-photo container then <img>
            img_src = None

            # Look for the <img> with ORICON's CDN pattern
            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                # Pick the first that matches ORICON news CDN
                if img_pattern.match(src):
                    img_src = src
                    break

            if img_src and img_src not in seen:
                seen.add(img_src)
                ordered_urls.append(img_src)
                print("Found:", img_src)

            # Find the 'next' arrow link
            next_a = soup.select_one("a.main_photo_next")
            if not next_a or not next_a.get("href"):
                # Fallback: any anchor with class containing 'main_photo_next'
                next_a = soup.find("a", class_=lambda c: c and "main_photo_next" in c)

            if next_a and next_a.get("href"):
                next_href = next_a["href"]
                url = urljoin(BASE, next_href)
                time.sleep(delay)
                continue
            else:
                # No next page link—stop
                break

        except Exception as e:
            print("Error parsing:", e)
            break

    print(f"Collected {len(ordered_urls)} image(s).")
    return ordered_urls

# ---------- Run ----------
if __name__ == "__main__":
    picture_url_list = parse_oricon_gallery(ORICON_NEWS_ID, ORICON_START_INDEX)
    total = len(picture_url_list)

    # Announce the gallery link (optional)
    start_page = f"https://www.oricon.co.jp/news/{ORICON_NEWS_ID}/photo/{ORICON_START_INDEX}/"
    send_telegram_message(start_page)

    for i, picture_url in enumerate(picture_url_list, start=1):
        # Try sending as link (Telegram fetches the URL).
        # If you see hotlinking errors in logs, switch to send_telegram_file_upload.
        send_telegram_file_link(f"{i}/{total}", picture_url)
        # Alternative (uncomment if above fails):
        # send_telegram_file_upload(f"{i}/{total}", picture_url)
