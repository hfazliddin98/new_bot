"""
Spam Himoyasi Test Script
"""
from telegram_bot.spam_protection import is_spam_message, validate_message

# Test xabarlar
test_messages = [
    "Salom, buyurtma bermoqchiman",  # ✅ OK
    "Menyu ko'rsating",  # ✅ OK
    "𝗠𝗲𝗴𝗮 / 𝗗𝗶𝗿𝗲𝗰𝘁 𝗟𝗶𝗻𝗸 / 𝗦𝘁𝗿𝗲𝗮𝗺 𝗙𝘂𝗹𝗹 𝗛𝗗 𝗣𝗢*𝗡",  # ❌ SPAM
    "https://t.me/Hot_Girlcc/3",  # ❌ SPAM
    "👇🏻👇🏻👇🏻👇🏻👇🏻👇🏻",  # ❌ SPAM (ko'p emoji)
]

print("🧪 Spam Himoyasi Test\n")
print("=" * 50)

for i, text in enumerate(test_messages, 1):
    is_spam = is_spam_message(text)
    status = "❌ SPAM" if is_spam else "✅ OK"
    
    print(f"\nTest #{i}: {status}")
    print(f"Xabar: {text[:50]}...")
    print("-" * 50)

print("\n✅ Test tugadi!")
