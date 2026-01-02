import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config.settings import TOKEN, EVENT_INTERVAL
from handlers.handlers import start, button_handler, transfer_points, handle_message
from features.events.events import daily_publisher
from admin.admin_panel import admin_command
from utils.logger import bot_logger

def main():
    bot_logger.info("--- بدء تشغيل Dragon Bot V2.0 ---")

    application = Application.builder().token(TOKEN).build()


    async def error_handler(update, context):
        try:
            bot_logger.exception(f"Unhandled exception for update: {update}")
        except Exception:
            pass

    # الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("transfer", transfer_points))
    application.add_handler(CommandHandler("admin", admin_command))

    # معالج الأزرار
    application.add_handler(CallbackQueryHandler(button_handler))

    # معالج الرسائل العامة
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # جدولة الفعاليات
    job_queue = application.job_queue
    job_queue.run_repeating(daily_publisher, interval=EVENT_INTERVAL, first=10)

    # مسجل الأخطاء العام
    application.add_error_handler(error_handler)

    bot_logger.info("--- Dragon Bot V2.0 جاهز للعمل ---")
    application.run_polling()

if __name__ == "__main__":
    main()
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("إضغط لتربح! ⚡️", callback_query_data="win_fast")]])
            await context.bot.send_message(chat_id, "🔥 فعالية السرعة! أول من يضغط على الزر يربح 100 نقطة!", reply_markup=btn)
        
        elif selected_event == "question":
            q = random.choice([
                {"q": "ما هو عاصمة السعودية؟", "a": "الرياض"},
                {"q": "كم عدد كواكب المجموعة الشمسية؟", "a": "8"},
                {"q": "مطور هذا البوت هو؟", "a": "احمد"}
            ])
            # منطق السؤال يحتاج لتخزين الإجابة في context.bot_data
            context.bot_data[f"q_{chat_id}"] = q["a"]
            await context.bot.send_message(chat_id, f"❓ سؤال سريع: {q['q']}\nأرسل الإجابة الصحيحة لتربح 50 نقطة!")

# --- معالجة الضغطات والأحداث ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data

    if data == "balance":
        u = get_user(user_id)
        await query.answer(f"رصيدك الحالي هو: {u['points']} نقطة 💰", show_alert=True)
    
    elif data == "about":
        text = (
            "🐉 **Dragon Bot V1.0**\n\n"
            "هذا البوت صُمم لزيادة التفاعل في المجموعات.\n"
            "• فعاليات يومية عشوائية.\n"
            "• متجر لبيع وشراء المنتجات الرقمية.\n"
            "• نظام نقاط آمن ومحمي.\n\n"
            f"👤 المطور: {DEVELOPER}\n"
            "⚙️ الحالة: قيد التطوير المستمر"
        )
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ عودة", callback_query_data="home")]])
        await query.edit_message_text(text, reply_markup=btn, parse_mode="Markdown")

    elif data == "home":
        await start(update, context)

    elif data == "referral":
        link = f"https://t.me/{(await context.bot.get_me()).username}?start={user_id}"
        u = get_user(user_id)
        text = (
            "🔗 **نظام الإحالة**\n\n"
            f"شارك الرابط الخاص بك وكن سبباً في دخول أعضاء جدد لتربح!\n"
            f"• لكل شخص يدخل عبر رابطك تحصل على **50 نقطة**.\n\n"
            f"عدد إحالاتك: {u['referrals']}\n"
            f"رابطك: `{link}`"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

    elif data == "win_fast":
        if "fast_won" not in context.bot_data:
            context.bot_data["fast_won"] = True
            db["users"][user_id]["points"] += 100
            save_db(db)
            await query.answer("مبروك! لقد كنت الأسرع وربحت 100 نقطة! 🎉")
            await query.edit_message_text(f"✅ انتهت الفعالية! الفائز هو {query.from_user.first_name}")
            # إعادة تعيين للفعلية القادمة بعد وقت
            await asyncio.sleep(60)
            context.bot_data.pop("fast_won", None)
        else:
            await query.answer("للأسف، شخص آخر كان أسرع منك! 💔")

    elif data.startswith("store_"):
        mode = data.split("_")[1]
        store_type = "الرسمي 🏢" if mode == "official" else "العام 🏪"
        items = db["official_store"] if mode == "official" else db["public_store"]
        
        text = f"🛒 **مرحباً بك في المتجر {store_type}**\n\n"
        if not items:
            text += "لا توجد منتجات حالياً."
        
        keyboard = []
        for idx, item in enumerate(items):
            keyboard.append([InlineKeyboardButton(f"{item['name']} - {item['price']}💰", callback_query_data=f"buy_{mode}_{idx}")])
        
        if mode == "public":
            keyboard.append([InlineKeyboardButton("➕ أضف منتجك للبيع", callback_query_data="add_item")])
        
        keyboard.append([InlineKeyboardButton("⬅️ عودة", callback_query_data="home")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# --- نظام تحويل النقاط (أمر نصي) ---
async def transfer_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("❌ الصيغة خاطئة. استخدم: `/transfer [الآيدي] [الكمية]`")
        return

    target_id = context.args[0]
    try:
        amount = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ الكمية يجب أن تكون رقماً.")
        return

    sender_id = str(update.effective_user.id)
    if amount <= 0:
        await update.message.reply_text("❌ الكمية غير صالحة.")
        return

    if db["users"].get(sender_id, {}).get("points", 0) < amount:
        await update.message.reply_text("❌ ليس لديك نقاط كافية.")
        return

    if target_id not in db["users"]:
        await update.message.reply_text("❌ هذا المستخدم غير مسجل في البوت.")
        return

    db["users"][sender_id]["points"] -= amount
    db["users"][target_id]["points"] += amount
    save_db(db)
    
    await update.message.reply_text(f"✅ تم تحويل {amount} نقطة إلى {target_id} بنجاح!")
    try:
        await context.bot.send_message(chat_id=target_id, text=f"💰 وصلتك حوالة بقيمة {amount} نقطة من {update.effective_user.first_name}!")
    except:
        pass

# --- وظيفة تشغيل البوت ---
def main():
    application = Application.builder().token(TOKEN).build()

    # الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("transfer", transfer_points))
    
    # معالج الأزرار
    application.add_handler(CallbackQueryHandler(button_handler))

    # جدولة المهام (النشر العشوائي 4 مرات يومياً)
    job_queue = application.job_queue
    # مثال: نشر كل 6 ساعات (تغير للأوقات العشوائية برمجياً)
    job_queue.run_repeating(daily_publisher, interval=21600, first=10)

    print("--- Dragon Bot Started Successfully ---")
    application.run_polling()

if __name__ == "__main__":
    main()