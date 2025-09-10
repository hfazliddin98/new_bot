@echo off
title Yetkazib berish tizimi
color 0A

echo.
echo ========================================
echo    YETKAZIIB BERISH TIZIMI
echo ========================================
echo.

echo 🚀 Tizim ishga tushirilmoqda...

REM Django server ishga tushirish
echo 🌐 Django server ishga tushirilmoqda...
start "Django Server" cmd /k ".venv\Scripts\python.exe manage.py runserver"

REM 5 soniya kutish
echo ⏳ 5 soniya kutish...
timeout /t 5 /nobreak > nul

REM Telegram bot ishga tushirish  
echo 🤖 Telegram bot ishga tushirilmoqda...
start "Telegram Bot" cmd /k ".venv\Scripts\python.exe manage.py runbot"

echo.
echo ✅ Barcha xizmatlar ishga tushdi!
echo.
echo 🌐 Web panel: http://127.0.0.1:8000
echo 👨‍🍳 Kitchen panel: http://127.0.0.1:8000/kitchen/
echo 🚛 Courier panel: http://127.0.0.1:8000/courier/
echo 🤖 Telegram bot: @ttjqdu_bot
echo.
echo Terminallarni yopish uchun har birida Ctrl+C bosing
echo.

pause
