# 📲 Twilio WhatsApp Media Sender

This Flask-based web app allows you to **send WhatsApp messages and media files** (like images, PDFs, MP4s, MP3s) using the Twilio API. It's a quick and user-friendly interface designed for demos, automation, or customer notification testing over WhatsApp.

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
