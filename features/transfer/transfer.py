from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import load_db, save_db, update_stats
from keyboards.keyboards import back_button
from utils.helpers import validate_amount

async def transfer_start(update, context):
    """بدء عملية التحويل"""
    query = update.callback_query
    text = (
        "💸 **نظام تحويل النقاط**\n\n"
        "📝 **كيفية التحويل:**\n"
        "استخدم الأمر: `/transfer [آيدي المستخدم] [الكمية]`\n\n"
        "📋 **مثال:**\n"
        "`/transfer 123456789 50`\n\n"
        "⚠️ **ملاحظات مهمة:**\n"
        "• تأكد من صحة الآيدي\n"
        "• لا يمكن التراجع عن التحويل\n"
        "• الحد الأدنى: 1 نقطة"
    )
    await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

async def transfer_points(update, context):
    """تنفيذ تحويل النقاط"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ **صيغة خاطئة!**\n\n"
            "استخدم: `/transfer [الآيدي] [الكمية]`\n"
            "مثال: `/transfer 123456789 50`",
            parse_mode="Markdown"
        )
        return

    target_id = context.args[0]
    valid, amount = validate_amount(context.args[1])

    if not valid:
        await update.message.reply_text("❌ الكمية يجب أن تكون رقماً صحيحاً وأكبر من صفر!")
        return

    sender_id = str(update.effective_user.id)
    db = load_db()

    if sender_id not in db["users"]:
        await update.message.reply_text("❌ يجب التسجيل أولاً!")
        return

    if target_id not in db["users"]:
        await update.message.reply_text("❌ المستخدم المستهدف غير مسجل في البوت!")
        return

    sender = db["users"][sender_id]
    if sender["points"] < amount:
        await update.message.reply_text("❌ ليس لديك نقاط كافية!")
        return

    # تنفيذ التحويل
    sender["points"] -= amount
    db["users"][target_id]["points"] += amount
    save_db(db)

    update_stats("total_transfers", db["stats"]["total_transfers"] + 1)

    await update.message.reply_text(
        f"✅ **تم التحويل بنجاح!**\n\n"
        f"📤 المرسل إليه: {target_id}\n"
        f"💰 الكمية: {amount} نقطة\n"
        f"💳 رصيدك المتبقي: {sender['points']} نقطة",
        parse_mode="Markdown"
    )

    # إشعار للمستلم
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=f"💰 **وصلتك حوالة جديدة!**\n\n"
                 f"📥 من: {update.effective_user.first_name}\n"
                 f"💸 الكمية: {amount} نقطة\n"
                 f"💰 رصيدك الجديد: {db['users'][target_id]['points']} نقطة",
            parse_mode="Markdown"
        )
    except:
        pass