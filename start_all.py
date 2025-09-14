#!/usr/bin/env python
"""
Django server va Telegram botni bir vaqtda ishga tushirish
"""
import os
import sys
import subprocess
import threading
import time
from pathlib import Path

# Virtual environment path
venv_python = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"

def run_django_server():
    """Django serverni ishga tushirish"""
    try:
        print("🌐 Django server ishga tushirilmoqda...")
        cmd = [str(venv_python), "manage.py", "runserver", "--noreload"]
        subprocess.run(cmd, cwd=Path(__file__).parent)
    except Exception as e:
        print(f"❌ Django server xatosi: {e}")

def run_telegram_bot():
    """Telegram botni ishga tushirish"""
    try:
        print("🤖 Telegram bot ishga tushirilmoqda...")
        time.sleep(5)  # Django serverning to'liq yuklanishini kutish
        cmd = [str(venv_python), "manage.py", "runbot"]
        subprocess.run(cmd, cwd=Path(__file__).parent)
    except Exception as e:
        print(f"❌ Telegram bot xatosi: {e}")

def main():
    """Asosiy funksiya"""
    print("🚀 Yetkazib berish tizimi ishga tushmoqda...")
    print("=" * 50)
    
    # Django server va bot uchun threadlar yaratish
    server_thread = threading.Thread(target=run_django_server, daemon=False)
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=False)
    
    try:
        # Threadlarni ishga tushirish
        server_thread.start()
        bot_thread.start()
        
        print("✅ Barcha xizmatlar ishga tushdi!")
        print("🌐 Web panel: http://127.0.0.1:8000")
        print("👨‍🍳 Kitchen panel: http://127.0.0.1:8000/kitchen/")
        print("🚛 Courier panel: http://127.0.0.1:8000/courier/")
        print("🤖 Telegram bot: @ttjqdu_bot")
        print("=" * 50)
        print("Ctrl+C tugmasi bilan to'xtatish mumkin")
        
        # Threadlar tugashini kutish
        server_thread.join()
        bot_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Tizim to'xtatildi!")
    except Exception as e:
        print(f"❌ Xatolik: {e}")

if __name__ == "__main__":
    main()
