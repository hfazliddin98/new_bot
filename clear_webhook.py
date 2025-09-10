#!/usr/bin/env python
"""
Bot tokenini tozalash va webhookni o'chirish
"""
import requests

BOT_TOKEN = "7305057883:AAG1iuNZK8dIhHXzTS_LV1dlMBneguVJW2Q"

def clear_webhook():
    """Webhookni o'chirish"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.get(url)
    print("Webhook o'chirildi:", response.json())

def get_me():
    """Bot ma'lumotlarini olish"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    response = requests.get(url)
    print("Bot ma'lumotlari:", response.json())

if __name__ == "__main__":
    clear_webhook()
    get_me()
