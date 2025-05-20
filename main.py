from flask import Flask, render_template, request, send_from_directory
from twilio.rest import Client
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max

# === Configuration via environment variables ===
NGROK_URL = os.getenv("NGROK_URL", "https://your-ngrok-url.ngrok-free.app")  # Update before use

# Allowed file types
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'mp4', 'mp3'}

# Twilio credentials and numbers from environment variables
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_NUMBER = os.getenv("TWILIO_NUMBER", "whatsapp:+1234567890")
MY_NUMBER = os.getenv("MY_WHATSAPP_NUMBER", "whatsapp:+1234567890")

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

client = Client(ACCOUNT_SID, AUTH_TOKEN)

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

        if (not message or message.strip() == '') and not media_url:
            return "❌ Please provide a message or upload a file.", 400

        msg_data = {
            'from_': TWILIO_NUMBER,
            'to': MY_NUMBER
        }

        if message and message.strip():
            msg_data['body'] = message.strip()

        if media_url:
            msg_data['media_url'] = [media_url]

        try:
            client.messages.create(**msg_data)
            return "✅ Message sent successfully!"
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ Failed to send message: {str(e)}", 500

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
