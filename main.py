from flask import Flask, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# === Environment config ===
NGROK_URL = os.getenv("NGROK_URL", "https://your-ngrok-url.ngrok-free.app")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "your_meta_access_token")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "your_phone_number_id")
RECIPIENT_PHONE = os.getenv("MY_WHATSAPP_NUMBER", "recipient_phone_number_including_country_code")  # e.g., 15551234567

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'mp4', 'mp3'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/check-upload/<filename>')
def check_upload(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception:
        return "File not found or inaccessible", 404

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        file = request.files.get('media_file')
        media_url = None

        if file and file.filename:
            if not allowed_file(file.filename):
                return "❌ Unsupported file type.", 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            media_url = f"{NGROK_URL}/uploads/{filename}"
            print(f"Media URL to send: {media_url}")

        if not message and not media_url:
            return "❌ Please provide a message or upload a file.", 400

        headers = {
            "Authorization": f"Bearer {WHATSAPP_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": RECIPIENT_PHONE,
            "type": "text",
            "text": {"body": message.strip()} if message else {"body": ""}
        }

        # If media is present, change type
        if media_url:
            file_ext = media_url.split('.')[-1].lower()

            if file_ext in ['jpg', 'jpeg', 'png']:
                payload["type"] = "image"
                payload["image"] = {"link": media_url, "caption": message or ""}
            elif file_ext == 'pdf':
                payload["type"] = "document"
                payload["document"] = {"link": media_url, "caption": message or ""}
            elif file_ext == 'mp4':
                payload["type"] = "video"
                payload["video"] = {"link": media_url, "caption": message or ""}
            elif file_ext == 'mp3':
                payload["type"] = "audio"
                payload["audio"] = {"link": media_url}
            else:
                return "❌ Unsupported media type.", 400

        try:
            url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                return "✅ Message sent successfully!"
            else:
                print(response.text)
                return f"❌ Failed: {response.status_code} - {response.text}", 500

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Error: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
