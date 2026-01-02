from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import get_user, add_points
from keyboards.keyboards import back_button
from config.settings import REFERRAL_REWARD

async def show_referral(update, context):
    """عرض نظام الإحالة"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    user = get_user(user_id)

    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    text = (
        "🔗 **نظام الإحالة الذهبي**\n\n"
        f"📈 **إحصائياتك:**\n"
        f"• عدد الإحالات: {user['referrals']}\n"
        f"• النقاط المكتسبة: {user['referrals'] * REFERRAL_REWARD}\n\n"
        f"🎁 **كيفية الربح:**\n"
        f"• لكل صديق ينضم عبر رابطك = **{REFERRAL_REWARD} نقطة**\n"
        f"• يمكنك مشاركة الرابط في أي مكان!\n\n"
        f"🔗 **رابطك الخاص:**\n"
        f"`{referral_link}`\n\n"
        f"📢 شارك الرابط وابدأ في كسب النقاط!"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📤 مشاركة الرابط", switch_inline_query=referral_link)],
        [InlineKeyboardButton("🏆 قائمة المحالات", callback_data="referral_list")],
        [InlineKeyboardButton("⬅️ عودة", callback_data="home")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def show_referral_list(update, context):
    """عرض قائمة المحالات"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    user = get_user(user_id)

    # في الواقع، نحتاج لتخزين قائمة المحالات في قاعدة البيانات
    # هذا مثال بسيط
    referrals = []  # يجب جلبها من قاعدة البيانات

    text = "🏆 **قائمة إحالاتك**\n\n"
    if not referrals:
        text += "📭 لم تقم بإحالة أي شخص بعد.\nابدأ الآن!"
    else:
        for i, ref in enumerate(referrals, 1):
            text += f"{i}. {ref['username']} - {ref['joined_at']}\n"

    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

async def process_referral(update, context, referrer_id):
    """معالجة الإحالة الجديدة"""
    user = update.effective_user
    user_id = str(user.id)

    user_data = get_user(user_id, user.username)

    if user_data["referred_by"] is None and referrer_id != user_id:
        user_data["referred_by"] = referrer_id
        # إضافة النقاط للمحيل
        add_points(referrer_id, REFERRAL_REWARD)
        # تحديث عدد الإحالات
        referrer_data = get_user(referrer_id)
        referrer_data["referrals"] += 1

        # إشعار للمحيل
        try:
            await context.bot.send_message(
                chat_id=referrer_id,
                text=f"🎉 **إحالة جديدة!**\n\n"
                     f"قام {user.first_name} بالانضمام عبر رابطك!\n"
                     f"حصلت على {REFERRAL_REWARD} نقطة إضافية!",
                parse_mode="Markdown"
            )
        except:
            pass