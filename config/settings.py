import os
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# --- إعدادات البوت ---
TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")  # استخدم متغير البيئة للأمان
ADMIN_ID = int(os.getenv("ADMIN_ID", "8049455831"))  # ضع الآيدي الخاص بك هنا
DEVELOPER = "@ahmaddragon"
VERSION = "2.0"  # تحديث الإصدار

# --- إعدادات قاعدة البيانات ---
DB_FILE = "dragon_db.json"

# --- إعدادات الفعاليات ---
EVENT_INTERVAL = 21600  # كل 6 ساعات
FAST_WIN_POINTS = 100
QUESTION_WIN_POINTS = 50
REFERRAL_REWARD = 50

# --- قائمة الأسئلة للفعاليات ---
QUESTIONS = [
    {"q": "ما هو عاصمة السعودية؟", "a": "الرياض"},
    {"q": "كم عدد كواكب المجموعة الشمسية؟", "a": "8"},
    {"q": "مطور هذا البوت هو؟", "a": "احمد"},
    {"q": "ما هو أكبر كوكب في المجموعة الشمسية؟", "a": "المشتري"},
    {"q": "ما هو لغة البرمجة المستخدمة في هذا البوت؟", "a": "Python"}
]

# --- قنوات ومجموعات للنشر (أضف آيديات هنا) ---
CHATS_TO_POST = []  # مثال: [-1001234567890, -1009876543210]