from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🏆 الفعاليات والمسابقات", callback_data="events")],
        [InlineKeyboardButton("💰 رصيدي", callback_data="balance"), InlineKeyboardButton("💸 تحويل نقاط", callback_data="transfer")],
        [InlineKeyboardButton("🏪 المتجر العام", callback_data="store_public"), InlineKeyboardButton("🏢 المتجر الرسمي", callback_data="store_official")],
        [InlineKeyboardButton("🔗 نظام الإحالة", callback_data="referral"), InlineKeyboardButton("⚙️ حول البوت", callback_data="about")],
        [InlineKeyboardButton("🎮 الألعاب والتحديات", callback_data="games"), InlineKeyboardButton("📊 إحصائياتي", callback_data="stats")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 إدارة المستخدمين", callback_data="admin_users")],
        [InlineKeyboardButton("📈 الإحصائيات العامة", callback_data="admin_stats")],
        [InlineKeyboardButton("💰 إضافة نقاط", callback_data="admin_add_points")],
        [InlineKeyboardButton("📢 إرسال إعلان", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🏪 إدارة المتجر", callback_data="admin_store")],
        [InlineKeyboardButton("⬅️ عودة للقائمة الرئيسية", callback_data="home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def back_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ عودة", callback_data="home")]])

def games_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎯 لعبة التخمين", callback_data="game_guess")],
        [InlineKeyboardButton("🧠 ألغاز", callback_data="game_puzzle")],
        [InlineKeyboardButton("⚡ تحدي السرعة", callback_data="game_speed")],
        [InlineKeyboardButton("⬅️ عودة", callback_data="home")]
    ]
    return InlineKeyboardMarkup(keyboard)

def store_keyboard(items, mode, can_add=True):
    keyboard = []
    for idx, item in enumerate(items):
        keyboard.append([InlineKeyboardButton(f"🛒 {item['name']} - {item['price']}💰", callback_data=f"buy_{mode}_{idx}")])
    
    if can_add and mode == "public":
        keyboard.append([InlineKeyboardButton("➕ أضف منتجك للبيع", callback_data="add_item")])
    
    keyboard.append([InlineKeyboardButton("⬅️ عودة", callback_data="home")])
    return InlineKeyboardMarkup(keyboard)