# 📲 Twilio WhatsApp Media Sender

This Flask-based web app allows you to **send WhatsApp messages and media files** (like images, PDFs, MP4s, MP3s) using the Twilio API. It's a quick and user-friendly interface designed for demos, automation, or customer notification testing over WhatsApp.

---

---

### ⚠️ Important Cleanup Step

Before running the application for the first time, **please delete the placeholder files** `a.txt` and `b.txt` located in the `media` and `uploads` directories respectively. These files are included for demonstration purposes but can interfere with file upload handling and media serving.

You can delete these files manually through your file explorer or command line. Removing them ensures the app works smoothly with fresh user uploads.

---

## 🚀 Project Description

This project lets you:

- Send WhatsApp messages using Twilio
- Upload and send media files (image, audio, video, documents)
- Easily test message delivery from a simple web interface
- Automatically generate `media_url` using your public Ngrok tunnel
- Logs file uploads for manual checking

It's especially useful for:

- Developers building WhatsApp integrations
- QA teams testing Twilio message delivery
- Automating basic notification workflows

---

## 📦 Features

- ✅ Send plain text messages
- ✅ Upload and attach media (JPG, PNG, MP4, MP3, PDF)
- ✅ Flask backend with basic upload handling
- ✅ Ngrok integration for publicly accessible media URLs
- ✅ Secure: All credentials are handled via `.env` file

---

## 🛠️ Setup Instructions

### 1. 🔧 Clone the repository

```bash
git clone https://github.com/AruGPT/Twilio-WhatsApp-Client-Portal.git
cd Twilio-WhatsApp-Client-Portal

