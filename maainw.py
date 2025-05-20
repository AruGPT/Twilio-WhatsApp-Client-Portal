import os
import time
import mimetypes
import requests
import pyperclip
import platform
import subprocess
from datetime import datetime
from twilio.rest import Client

# === Twilio credentials (use environment variables or secure storage) ===
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid_here")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token_here")
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# === Files and folders ===
LOG_FILE = "message_log.txt"
SEEN_SIDS_FILE = "seen_sids.txt"
MEDIA_ROOT_FOLDER = "media"
os.makedirs(MEDIA_ROOT_FOLDER, exist_ok=True)

# === Load seen message SIDs ===
seen_sids = set()
if os.path.exists(SEEN_SIDS_FILE):
    with open(SEEN_SIDS_FILE, "r", encoding="utf-8") as f:
        seen_sids = set(line.strip() for line in f if line.strip())

# === Logging function (console + file) ===
def log(text, newline=True):
    timestamp = f"[{datetime.now()}]"
    line = f"{timestamp} {text}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(line + ("\n" if newline else ""))
        log_file.flush()

# === Log message to file only ===
def log_message(entry):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{datetime.now()}] SID: {entry['SID']}\n")
        log_file.write(f"  From: {entry['From']}\n")
        log_file.write(f"  To: {entry['To']}\n")
        log_file.write(f"  Date Sent: {entry['Date Sent']}\n")
        log_file.write(f"  Body: {entry['Body'] or '(No text)'}\n")
        if entry.get("Media"):
            log_file.write("  Media files:\n")
            for media_path in entry["Media"]:
                log_file.write(f"    - {media_path}\n")
        else:
            log_file.write("  Media files: None\n")
        log_file.write("\n")
        log_file.flush()

# === Log message to console ===
def log_message_console(entry):
    timestamp = f"[{datetime.now()}]"
    print(f"{timestamp} SID: {entry['SID']}")
    print(f"  From: {entry['From']}")
    print(f"  To: {entry['To']}")
    print(f"  Date Sent: {entry['Date Sent']}")
    print(f"  Body: {entry['Body'] or '(No text)'}")
    if entry.get("Media"):
        print("  Media files:")
        for media_path in entry["Media"]:
            print(f"    - {media_path}")
    else:
        print("  Media files: None")
    print()  # blank line

# === Save SID ===
def save_seen_sid(sid):
    with open(SEEN_SIDS_FILE, "a", encoding="utf-8") as f:
        f.write(sid + "\n")

# === Open folder ===
def open_folder(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        log(f"[WARNING] Could not open folder {path}: {e}")

# === Download media ===
def download_media_files(message_sid, message_date):
    media_paths = []
    try:
        media_list = client.messages(message_sid).media.list()
        date_folder = os.path.join(MEDIA_ROOT_FOLDER, message_date)
        sid_folder = os.path.join(date_folder, message_sid)
        os.makedirs(sid_folder, exist_ok=True)

        for media in media_list:
            media_sid = media.sid
            media_url = f"https://api.twilio.com{media.uri.replace('.json', '')}"
            ext = mimetypes.guess_extension(media.content_type) or ".bin"
            filename = f"{media_sid}{ext}"
            filepath = os.path.join(sid_folder, filename)

            response = requests.get(media_url, auth=(ACCOUNT_SID, AUTH_TOKEN))

            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                abs_path = os.path.abspath(filepath)
                media_paths.append(abs_path)

        if media_paths:
            open_folder(sid_folder)

    except Exception:
        pass  # silently ignore exceptions here
    return media_paths

# === Start polling ===
log("📡 Starting Twilio message logger...")
log(f"[INFO] Log file: {os.path.abspath(LOG_FILE)}")
log(f"[INFO] Media folder: {os.path.abspath(MEDIA_ROOT_FOLDER)}")
log(f"[INFO] Loaded {len(seen_sids)} seen SIDs.")

last_no_msg_time = 0  # To control how often "no new messages" is logged

while True:
    try:
        messages = client.messages.list(limit=50)
        new_messages_found = False

        for msg in messages:
            if msg.sid not in seen_sids:
                new_messages_found = True
                entry = {
                    "SID": msg.sid,
                    "From": msg.from_,
                    "To": msg.to,
                    "Date Sent": str(msg.date_sent),
                    "Body": msg.body,
                    "Media": []
                }

                message_date = msg.date_sent.strftime("%Y-%m-%d") if msg.date_sent else "unknown_date"
                if int(msg.num_media) > 0:
                    media_paths = download_media_files(msg.sid, message_date)
                    if media_paths:
                        pyperclip.copy("\n".join(media_paths))
                        entry["Media"] = media_paths

                log(f"[INFO] New message found: SID={msg.sid}")
                log_message(entry)
                log_message_console(entry)

                save_seen_sid(msg.sid)
                seen_sids.add(msg.sid)

        # Log only once per 60 seconds if no messages
        if not new_messages_found:
            now = time.time()
            if now - last_no_msg_time >= 60:
                log("↺ No new messages.")
                last_no_msg_time = now

    except Exception as e:
        log(f"ERROR checking messages: {e}")

    time.sleep(10)
