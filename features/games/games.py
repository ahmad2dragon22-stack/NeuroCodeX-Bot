import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from database.db_manager import add_points, get_user
from keyboards.keyboards import back_button

async def show_games_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الألعاب"""
    from keyboards.keyboards import games_menu_keyboard
    text = (
        "🎮 **ألعاب وتحديات Dragon Bot**\n\n"
        "اختر اللعبة التي تريد اللعبها:\n\n"
        "🎯 **لعبة التخمين**: خمن الرقم الصحيح\n"
        "🧠 **الألغاز**: حل الألغاز الذكية\n"
        "⚡ **تحدي السرعة**: اختبر ردود أفعالك\n\n"
        "💰 كل فوز يمنحك نقاطاً إضافية!"
    )
    await update.callback_query.edit_message_text(text, reply_markup=games_menu_keyboard(), parse_mode="Markdown")

async def start_guess_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء لعبة التخمين"""
    user_id = str(update.callback_query.from_user.id)
    secret_number = random.randint(1, 100)
    context.user_data[f"guess_{user_id}"] = {"number": secret_number, "attempts": 0, "max_attempts": 7}

    keyboard = []
    for i in range(1, 101, 10):
        row = []
        for j in range(i, min(i+10, 101)):
            row.append(InlineKeyboardButton(str(j), callback_data=f"guess_{j}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("⬅️ إلغاء", callback_data="games")])

    text = (
        "🎯 **لعبة التخمين**\n\n"
        "خمن الرقم السري من 1 إلى 100!\n"
        "لديك 7 محاولات فقط.\n\n"
        "💰 الجائزة: 50 نقطة للفوز الأول\n"
        "        25 نقطة للفوز الثاني\n"
        "        10 نقاط للفوز الثالث"
    )
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_guess(update: Update, context: ContextTypes.DEFAULT_TYPE, guess: int):
    """معالجة تخمين المستخدم"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    game_data = context.user_data.get(f"guess_{user_id}")

    if not game_data:
        await query.answer("ليس لديك لعبة جارية!", show_alert=True)
        return

    game_data["attempts"] += 1
    secret = game_data["number"]

    if guess == secret:
        # فوز
        attempts = game_data["attempts"]
        if attempts == 1:
            points = 50
        elif attempts <= 3:
            points = 25
        else:
            points = 10

        add_points(user_id, points)
        await query.edit_message_text(
            f"🎉 **مبروك! فزت!**\n\n"
            f"الرقم الصحيح كان: {secret}\n"
            f"عدد المحاولات: {attempts}\n"
            f"💰 ربحت: {points} نقطة\n\n"
            f"⭐ استمر في اللعب لتحسين مهارتك!",
            reply_markup=back_button(),
            parse_mode="Markdown"
        )
        context.user_data.pop(f"guess_{user_id}", None)

    elif game_data["attempts"] >= game_data["max_attempts"]:
        # خسارة
        await query.edit_message_text(
            f"😔 **خسرت!**\n\n"
            f"الرقم الصحيح كان: {secret}\n"
            f"لا تيأس، جرب مرة أخرى!",
            reply_markup=back_button(),
            parse_mode="Markdown"
        )
        context.user_data.pop(f"guess_{user_id}", None)

    else:
        # استمرار
        hint = "أكبر" if guess < secret else "أصغر"
        remaining = game_data["max_attempts"] - game_data["attempts"]
        await query.answer(f"{hint}! محاولات متبقية: {remaining}", show_alert=True)

async def start_puzzle_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء لعبة الألغاز"""
    puzzles = [
        {"question": "ما هو الشيء الذي يمشي بأربع أرجل صباحاً، اثنتين ظهراً، وثلاث مساءً؟", "answer": "الإنسان"},
        {"question": "ما هو الشيء الذي يأكل ويشرب لكنه لا يحتاج إلى فم؟", "answer": "النار"},
        {"question": "ما هو البيت الذي لا يسكنه أحد؟", "answer": "القبر"},
    ]

    puzzle = random.choice(puzzles)
    user_id = str(update.callback_query.from_user.id)
    context.user_data[f"puzzle_{user_id}"] = puzzle["answer"].lower()

    text = (
        "🧠 **لغز ذكي**\n\n"
        f"**{puzzle['question']}**\n\n"
        "اكتب إجابتك في رسالة منفصلة!\n"
        "💰 الجائزة: 30 نقطة"
    )
    await update.callback_query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

async def check_puzzle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """فحص إجابة اللغز"""
    user = update.effective_user
    user_id = str(user.id)
    answer = update.message.text.lower().strip()

    correct_answer = context.user_data.get(f"puzzle_{user_id}")
    if correct_answer and answer == correct_answer:
        add_points(user_id, 30)
        await update.message.reply_text(
            f"🎉 إجابة صحيحة يا {user.first_name}!\n"
            "ربحت 30 نقطة! 🧠",
            parse_mode="Markdown"
        )
        context.user_data.pop(f"puzzle_{user_id}", None)
    elif correct_answer:
        await update.message.reply_text("❌ إجابة خاطئة. جرب مرة أخرى!")

async def start_speed_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء تحدي السرعة"""
    user_id = str(update.callback_query.from_user.id)
    context.user_data[f"speed_{user_id}"] = {"start_time": None, "waiting": True}

    text = (
        "⚡ **تحدي السرعة**\n\n"
        "اضغط على الزر في أسرع وقت ممكن عندما يظهر!\n\n"
        "⚠️ استعد..."
    )
    keyboard = [[InlineKeyboardButton("🚀 جاهز!", callback_data="speed_ready")]]
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_speed_ready(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الاستعداد للتحدي"""
    import time
    user_id = str(update.callback_query.from_user.id)
    delay = random.uniform(2, 5)  # انتظار عشوائي

    await asyncio.sleep(delay)

    context.user_data[f"speed_{user_id}"] = {"start_time": time.time(), "waiting": False}

    keyboard = [[InlineKeyboardButton("⚡ اضغط الآن!", callback_data="speed_click")]]
    try:
        await update.callback_query.edit_message_text(
            "⚡ **الآن! اضغط بأسرع ما يمكن!** ⚡",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except:
        pass

async def handle_speed_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة النقر في تحدي السرعة"""
    import time
    query = update.callback_query
    user_id = str(query.from_user.id)
    game_data = context.user_data.get(f"speed_{user_id}")

    if not game_data or game_data["waiting"]:
        await query.answer("انتظر الإشارة!", show_alert=True)
        return

    reaction_time = time.time() - game_data["start_time"]

    if reaction_time < 0.2:
        points = 50
        result = "⚡ خارق السرعة!"
    elif reaction_time < 0.5:
        points = 30
        result = "🚀 سريع جداً!"
    elif reaction_time < 1.0:
        points = 15
        result = "💨 سريع!"
    else:
        points = 5
        result = "🐌 يمكن تحسينه"

    add_points(user_id, points)

    await query.edit_message_text(
        f"🎯 **نتيجتك في تحدي السرعة**\n\n"
        f"⏱️ زمن رد الفعل: {reaction_time:.3f} ثانية\n"
        f"{result}\n"
        f"💰 ربحت: {points} نقطة\n\n"
        f"جرب مرة أخرى لتحطيم الرقم القياسي!",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )
    context.user_data.pop(f"speed_{user_id}", None)