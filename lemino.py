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
            else:
                print(response_body)
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


def send_telegram_document_link_save_first(caption, file_link):
    local_filename = file_link.split("/")[-1]

    try:
        # 先下载文件
        with requests.get(file_link, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 发送文件到 Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        with open(local_filename, "rb") as doc_file:
            files = {"document": doc_file}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML",
            }
            while True:
                try:
                    response = requests.post(url, data=data, files=files)
                    response_body = response.json()
                    # print(response_body)  # 可选：调试用
                    if "error_code" not in response_body:
                        break
                    else:
                        time.sleep(5)
                        break
                except Exception as e:
                    print(e)
                    time.sleep(5)
                    continue
    except Exception as download_err:
        print(f"Download error: {download_err}")
    finally:
        # 删除临时文件
        if os.path.exists(local_filename):
            os.remove(local_filename)


def send_telegram_photo_link_save_first(caption, file_link):
    local_filename = file_link.split("/")[-1]

    try:
        # 先下载文件
        with requests.get(file_link, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # 发送文件到 Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        with open(local_filename, "rb") as doc_file:
            files = {"photo": doc_file}
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "HTML",
            }
            while True:
                try:
                    response = requests.post(url, data=data, files=files)
                    response_body = response.json()
                    # print(response_body)  # 可选：调试用
                    if "error_code" not in response_body:
                        break
                    else:
                        time.sleep(5)
                        break
                except Exception as e:
                    print(e)
                    time.sleep(5)
                    continue
    except Exception as download_err:
        print(f"Download error: {download_err}")
    finally:
        # 删除临时文件
        if os.path.exists(local_filename):
            os.remove(local_filename)


def get_send(id, start):
    consecutive_not_found = 0
    for i in range(start, 9999):
        url = f"https://lemino.docomo.ne.jp/ft/{id}/images/cntents_{i}.webp"
        response = requests.head(url)
        if response.status_code == 200:
            print(f"Image URL: {url}")
            send_telegram_photo_link_save_first(f"Image URL: {url}", url)
            # send_telegram_document_link_save_first(f"Image URL: {url}", url)
        else:
            print(f"No images found for {url}")
            consecutive_not_found += 1
        # time.sleep(5)
        if consecutive_not_found >= 2:
            print("No more images found, stopping.")
            print("Finished sending images.")
            break


get_send("0000013", 39)
get_send("0000045", 30)
get_send("0000046", 23)
