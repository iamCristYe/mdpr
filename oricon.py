from bs4 import BeautifulSoup
import requests
import os
import time
import re
from urllib.parse import urljoin

TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_THREAD_ID = os.environ.get("TELEGRAM_THREAD_ID")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

ORICON_NEWS_ID = os.environ.get("ORICON_NEWS_ID", "2443390")  # example: 2443390
ORICON_START_INDEX = int(os.environ.get("ORICON_START_INDEX", "1"))



# ---------- Your existing Telegram helpers (kept same behavior, no sleep) ----------


def send_telegram_file_link(caption, file_link):
    max_retries = 5
    attempt = 0

    while attempt < max_retries:
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
            body = response.json()
            if "error_code" not in body:
                return True
            else:
                # Print for diagnostics; still return False to trigger fallback if desired
                print("sendDocument link error:", body)
                return False
        except Exception as e:
            print(e)
            # Try again (you can add a counter if you want to limit retries)
            time.sleep(20)
            attempt += 1


def send_telegram_message(text):
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
            }
            if TELEGRAM_THREAD_ID is not None:
                payload["message_thread_id"] = TELEGRAM_THREAD_ID
            response = requests.post(url, data=payload, timeout=30)
            body = response.json()
            if "error_code" not in body:
                return True
            else:
                print("sendMessage error:", body)
                return False
        except Exception as e:
            print(e)
            time.sleep(1)
            pass


# Optional: fallback upload to bypass hotlink protection
def send_telegram_file_upload(caption, img_url):
    while True:
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Referer": "https://www.oricon.co.jp/",
            }
            r = requests.get(img_url, headers=headers, timeout=60)
            r.raise_for_status()

            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
            files = {"document": ("photo.jpg", r.content, "image/jpeg")}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML",
            }
            if TELEGRAM_THREAD_ID is not None:
                data["message_thread_id"] = TELEGRAM_THREAD_ID

            response = requests.post(url, data=data, files=files, timeout=120)
            body = response.json()
            if "error_code" not in body:
                return True
            else:
                print("sendDocument upload error:", body)
                return False
        except Exception as e:
            print(e)
            time.sleep(1)
            pass


# ---------- STREAMING CRAWLER: find one -> send one ----------


def stream_oricon_and_send(
    news_id, start_index=1, polite_delay=0.2, use_upload_fallback=True
):
    """
    Crawl ORICON gallery starting at /news/{news_id}/photo/{start_index}/.
    For each page:
      - extract the main image URL,
      - SEND IMMEDIATELY to Telegram,
      - then follow the 'next' arrow.
    Stops if HTTP error or 'not found' title is detected.
    """
    BASE = "https://www.oricon.co.jp"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    }
    error_title = "該当するページが見つかりません | ORICON NEWS"
    img_pattern = re.compile(r"^https://contents\.oricon\.co\.jp/upimg/news/")

    url = f"{BASE}/news/{news_id}/photo/{start_index}/"
    index = start_index

    # (Optional) announce the gallery entry
    send_telegram_message(url)

    while True:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code >= 400:
                print(f"Stop: HTTP {resp.status_code} at {url}")
                break

            soup = BeautifulSoup(resp.text, "lxml")

            # Stop on not-found page (even if status=200)
            title_text = soup.title.get_text(strip=True) if soup.title else ""
            if (
                title_text == error_title
                or "該当するページが見つかりません" in title_text
            ):
                print(f"Stop: Not-found page at {url}")
                break

            # Extract the main image for this page
            img_src = None
            for img in soup.find_all("img", src=True):
                src = img["src"].strip()
                if img_pattern.match(src):
                    img_src = src
                    break

            if img_src:
                caption = f"{index}"
                ok = send_telegram_file_link(caption, img_src)
                if not ok and use_upload_fallback:
                    # fallback to upload to bypass hotlink
                    _ = send_telegram_file_upload(caption, img_src)
                print("Sent:", img_src)
            else:
                print(f"No image found on {url} — stopping.")
                break

            # Find the next page link
            # next_a = soup.select_one("a.main_photo_next")
            # if not next_a or not next_a.get("href"):
            #     next_a = soup.find("a", class_=lambda c: c and "main_photo_next" in c)

            # if next_a and next_a.get("href"):
            #     next_href = next_a["href"]
            index += 1
            url = f"{BASE}/news/{news_id}/photo/{index}/"

            # Polite delay between page fetches (doesn't delay sending)
            if polite_delay > 0:
                time.sleep(polite_delay)
            #     continue
            # else:
            #     print("No next link — done.")
            #     break

        except Exception as e:
            print("Error:", e)
            break


if __name__ == "__main__":
    stream_oricon_and_send(ORICON_NEWS_ID, ORICON_START_INDEX)
