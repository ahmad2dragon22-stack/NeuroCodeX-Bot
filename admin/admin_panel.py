from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import load_db, save_db, get_stats, add_points
from keyboards.keyboards import admin_menu_keyboard, back_button
from config.settings import ADMIN_ID

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر الإدارة"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ غير مصرح لك بالوصول إلى لوحة التحكم!")
        return

    await show_admin_panel(update, context)
    """عرض لوحة التحكم للإدارة"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.callback_query.answer("❌ غير مصرح لك بالوصول!", show_alert=True)
        return

    query = update.callback_query
    stats = get_stats()

    text = (
        "🔧 **لوحة التحكم الإدارية**\n\n"
        f"📊 **إحصائيات سريعة:**\n"
        f"👥 المستخدمون: {stats['total_users']}\n"
        f"🎯 الفعاليات: {stats['total_events']}\n"
        f"💸 التحويلات: {stats['total_transfers']}\n\n"
        f"⚙️ اختر العملية المطلوبة:"
    )

    await query.edit_message_text(text, reply_markup=admin_menu_keyboard(), parse_mode="Markdown")

async def admin_stats(update, context):
    """عرض الإحصائيات التفصيلية"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        return

    db = load_db()
    stats = db["stats"]
    users = db["users"]

    total_points = sum(user["points"] for user in users.values())
    active_users = sum(1 for user in users.values() if user.get("last_active"))

    text = (
        "📈 **الإحصائيات التفصيلية**\n\n"
        f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
        f"🎯 إجمالي الفعاليات: {stats['total_events']}\n"
        f"💸 إجمالي التحويلات: {stats['total_transfers']}\n"
        f"💰 إجمالي النقاط في النظام: {total_points}\n"
        f"🔥 المستخدمون النشطون: {active_users}\n\n"
        f"🏪 منتجات المتجر العام: {len(db['public_store'])}\n"
        f"🏢 منتجات المتجر الرسمي: {len(db['official_store'])}"
    )

    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

async def admin_add_points_start(update, context):
    """بدء إضافة نقاط لمستخدم"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        return

    context.user_data["admin_action"] = "add_points"
    await query.edit_message_text(
        "💰 **إضافة نقاط لمستخدم**\n\n"
        "أرسل آيدي المستخدم:",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )

async def admin_add_points_id(update, context):
    """تلقي آيدي المستخدم"""
    if context.user_data.get("admin_action") != "add_points":
        return

    context.user_data["target_user"] = update.message.text
    context.user_data["step"] = "amount"
    await update.message.reply_text("💸 أرسل كمية النقاط المراد إضافتها:")

async def admin_add_points_amount(update, context):
    """تلقي كمية النقاط"""
    if context.user_data.get("step") != "amount":
        return

    valid, amount = validate_amount(update.message.text)
    if not valid:
        await update.message.reply_text("❌ الكمية يجب أن تكون رقماً صحيحاً!")
        return

    target_id = context.user_data["target_user"]
    add_points(target_id, amount)

    await update.message.reply_text(
        f"✅ **تم إضافة النقاط بنجاح!**\n\n"
        f"👤 المستخدم: {target_id}\n"
        f"💰 الكمية المضافة: {amount} نقطة",
        parse_mode="Markdown"
    )

    context.user_data.clear()

async def admin_broadcast_start(update, context):
    """بدء إرسال إعلان"""
    query = update.callback_query
    if query.from_user.id != ADMIN_ID:
        return

    context.user_data["admin_action"] = "broadcast"
    await query.edit_message_text(
        "📢 **إرسال إعلان جماعي**\n\n"
        "أرسل نص الإعلان:",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )

async def admin_broadcast_send(update, context):
    """إرسال الإعلان"""
    if context.user_data.get("admin_action") != "broadcast":
        return

    message = update.message.text
    db = load_db()
    sent_count = 0

    for user_id in db["users"]:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 **إعلان إداري**\n\n{message}",
                parse_mode="Markdown"
            )
            sent_count += 1
        except:
            pass

    await update.message.reply_text(
        f"✅ **تم إرسال الإعلان!**\n\n"
        f"📨 عدد المستلمين: {sent_count}",
        parse_mode="Markdown"
    )

    context.user_data.clear()

from utils.helpers import validate_amount