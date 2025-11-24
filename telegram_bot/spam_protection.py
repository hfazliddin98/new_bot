"""
Telegram Bot Spam Himoyasi
"""
import logging

logger = logging.getLogger(__name__)

# Qora ro'yxat (bloklangan foydalanuvchilar)
BLOCKED_USERS = set()

# Spam kalit so'zlari
SPAM_KEYWORDS = [
    'mega', 'direct link', 'stream', 'hot_girl', 'po*n', 'porn',
    't.me/', 'http://', 'https://', '👇', '👆', 'click here',
    'free download', 'full hd', 'xxx', '🔞', 'hot girl', 'sexy',
    'nude', 'naked', 'adult', '18+', 'only fans', 'onlyfans',
    'premium', 'vip channel', 'join now', 'subscribe'
]

# Spamerlar pattern'lari
SPAM_PATTERNS = [
    r't\.me/\w+',  # Telegram kanal/guruh linklari
    r'https?://.*',  # HTTP linklari
    r'[👇👆]{3,}',  # Ko'p ko'rsatkich emoji
    r'[🔞💋❤️😘]{3,}',  # Ko'p "hot" emoji
]

def is_spam_message(text: str) -> bool:
    """
    Xabar spam ekanligini tekshirish
    """
    if not text:
        return False
    
    text_lower = text.lower()
    
    # 1. Spam kalit so'zlarni tekshirish
    for keyword in SPAM_KEYWORDS:
        if keyword in text_lower:
            logger.warning(f"Spam keyword topildi: {keyword}")
            return True
    
    # 2. Ko'p emoji borligini tekshirish (10 dan ortiq)
    emoji_count = sum(1 for char in text if ord(char) > 127462)
    if emoji_count > 10:
        logger.warning(f"Ko'p emoji topildi: {emoji_count}")
        return True
    
    # 3. Ko'p link borligini tekshirish
    link_count = text.count('http://') + text.count('https://') + text.count('t.me/')
    if link_count > 1:
        logger.warning(f"Ko'p link topildi: {link_count}")
        return True
    
    # 4. Xabar juda uzun (spam odatda uzun bo'ladi)
    if len(text) > 1000:
        logger.warning(f"Juda uzun xabar: {len(text)} belgi")
        return True
    
    return False

def is_user_blocked(user_id: int) -> bool:
    """
    Foydalanuvchi bloklangan yoki yo'qligini tekshirish
    """
    return user_id in BLOCKED_USERS

def block_user(user_id: int):
    """
    Foydalanuvchini bloklash
    """
    BLOCKED_USERS.add(user_id)
    logger.info(f"Foydalanuvchi bloklandi: {user_id}")

def unblock_user(user_id: int):
    """
    Foydalanuvchini blokdan chiqarish
    """
    if user_id in BLOCKED_USERS:
        BLOCKED_USERS.remove(user_id)
        logger.info(f"Foydalanuvchi blokdan chiqarildi: {user_id}")

def is_private_chat(message) -> bool:
    """
    Xabar shaxsiy chatda yuborilganligini tekshirish
    """
    return message.chat.type == 'private'

def validate_message(message) -> tuple[bool, str]:
    """
    Xabarni to'liq validatsiya qilish
    
    Returns:
        (is_valid, error_message)
    """
    # 1. Faqat shaxsiy chat
    if not is_private_chat(message):
        return False, "Faqat shaxsiy chatda ishlaydi"
    
    # 2. Bloklangan foydalanuvchi
    if is_user_blocked(message.from_user.id):
        return False, "Foydalanuvchi bloklangan"
    
    # 3. Spam tekshirish
    if message.text and is_spam_message(message.text):
        # Avtomatik bloklash
        block_user(message.from_user.id)
        return False, "Spam xabar aniqlandi"
    
    return True, "OK"
