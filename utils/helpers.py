import random
from config.settings import QUESTIONS

def format_number(num):
    """تنسيق الأرقام بشكل جميل"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def get_random_question():
    """الحصول على سؤال عشوائي"""
    return random.choice(QUESTIONS)

def calculate_level(points):
    """حساب المستوى بناءً على النقاط"""
    levels = [
        (0, "مبتدئ 🐣"),
        (100, "متعلم 📚"),
        (500, "خبير 🎓"),
        (1000, "محترف 💼"),
        (2500, "خبير متمرس 🏆"),
        (5000, "أسطورة 🌟")
    ]
    for threshold, title in reversed(levels):
        if points >= threshold:
            return title
    return levels[0][1]

def validate_amount(amount_str):
    """التحقق من صحة الكمية"""
    try:
        amount = int(amount_str)
        return amount > 0, amount
    except ValueError:
        return False, 0

def escape_markdown(text):
    """تجنب الرموز الخاصة في Markdown"""
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text