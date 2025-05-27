import os
import json
import requests
import mimetypes
from flask import Flask, request, jsonify
from datetime import datetime

# === WhatsApp Cloud API Credentials ===
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # Replace with your real access token
VERIFY_TOKEN = "YOUR_VERIFY_TOKEN_HERE"  # Replace with your real verify token
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

# === Config ===
LOG_FILE = "message_log.txt"
MEDIA_FOLDER = "media"

# === Flask App ===
app = Flask(__name__)
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# === Logging Helper ===
def log(text):
    timestamp = f"[{datetime.now()}]"
    print(f"{timestamp} {text}")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {text}\n")

# === Download Media from WhatsApp ===
def download_media(media_id, mime_type):
    try:
        media_info = requests.get(
            f"https://graph.facebook.com/v19.0/{media_id}",
            headers=HEADERS
        ).json()
        media_url = media_info.get("url")
        if not media_url:
            return None

        response = requests.get(media_url, headers=HEADERS)
        ext = mimetypes.guess_extension(mime_type) or ".bin"
        filename = f"{media_id}{ext}"
        folder = os.path.join(MEDIA_FOLDER, datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        return os.path.abspath(filepath)
    except Exception as e:
        log(f"Error downloading media: {e}")
        return None

# === Webhook Verification ===
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403

# === Webhook Message Receiver ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    msg_type = msg.get("type")
                    from_number = msg.get("from")
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if msg_type == "text":
                        text = msg["text"]["body"]
                        log(f"[{timestamp}] Text from {from_number}: {text}")
                    elif msg_type in ["image", "audio", "video", "document", "sticker"]:
                        media_info = msg.get(msg_type, {})
                        media_id = media_info.get("id")
                        mime_type = media_info.get("mime_type", "application/octet-stream")
                        media_path = download_media(media_id, mime_type)
                        if media_path:
                            log(f"[{timestamp}] Media from {from_number}: {media_path}")
                        else:
                            log(f"[{timestamp}] Failed to download media from {from_number}")
                    else:
                        log(f"[{timestamp}] Unsupported message type: {msg_type}")
    except Exception as e:
        log(f"Webhook processing error: {e}")

    return jsonify({"status": "received"}), 200

# === Run the App ===
if __name__ == "__main__":
    app.run(port=5000, debug=True)
