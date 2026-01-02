import asyncio
import random
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import CHATS_TO_POST, FAST_WIN_POINTS, QUESTION_WIN_POINTS
from database.db_manager import add_points, update_stats
from utils.helpers import get_random_question

async def daily_publisher(context):
    """دالة تقوم بالنشر العشوائي للفعاليات"""
    if not CHATS_TO_POST:
        return  # لا توجد قنوات محددة

    event_types = ["fast_button", "question", "share_link", "mini_game"]
    selected_event = random.choice(event_types)

    for chat_id in CHATS_TO_POST:
        try:
            if selected_event == "fast_button":
                await send_fast_button_event(context, chat_id)
            elif selected_event == "question":
                await send_question_event(context, chat_id)
            elif selected_event == "share_link":
                await send_share_event(context, chat_id)
            elif selected_event == "mini_game":
                await send_mini_game_event(context, chat_id)
        except Exception as e:
            print(f"خطأ في نشر الفعالية في {chat_id}: {e}")

async def send_fast_button_event(context, chat_id):
    """فعالية الزر السريع"""
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("⚡ إضغط لتربح!", callback_data="win_fast")]])
    await context.bot.send_message(
        chat_id,
        "🔥 **فعالية السرعة الخارقة!**\n\n"
        "أول من يضغط على الزر يربح **100 نقطة**!\n"
        "⚠️ لديك 30 ثانية فقط!",
        reply_markup=btn,
        parse_mode="Markdown"
    )
    # إزالة الفعالية بعد 30 ثانية
    await asyncio.sleep(30)
    try:
        await context.bot.edit_message_reply_markup(chat_id, message_id=None, reply_markup=None)
    except:
        pass

async def send_question_event(context, chat_id):
    """فعالية السؤال السريع"""
    question = get_random_question()
    context.bot_data[f"q_{chat_id}"] = question["a"].lower()
    await context.bot.send_message(
        chat_id,
        f"❓ **سؤال سريع للجميع!**\n\n"
        f"**{question['q']}**\n\n"
        f"أرسل الإجابة الصحيحة لتربح **{QUESTION_WIN_POINTS} نقطة**!\n"
        f"⏰ لديك دقيقة واحدة.",
        parse_mode="Markdown"
    )
    # مسح السؤال بعد دقيقة
    await asyncio.sleep(60)
    context.bot_data.pop(f"q_{chat_id}", None)

async def send_share_event(context, chat_id):
    """فعالية مشاركة الرابط"""
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 شارك الآن", callback_data="share_link")]])
    await context.bot.send_message(
        chat_id,
        "📢 **فعالية المشاركة!**\n\n"
        "شارك رابط البوت مع أصدقائك واحصل على **25 نقطة**!\n"
        "كل مشاركة = نقاط إضافية!",
        reply_markup=btn,
        parse_mode="Markdown"
    )

async def send_mini_game_event(context, chat_id):
    """فعالية لعبة صغيرة"""
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎮 العب الآن", callback_data="mini_game_start")]])
    await context.bot.send_message(
        chat_id,
        "🎲 **لعبة التخمين السريع!**\n\n"
        "خمن الرقم من 1 إلى 10 واحصل على جوائز!\n"
        "الفائز يحصل على **75 نقطة**!",
        reply_markup=btn,
        parse_mode="Markdown"
    )

async def handle_fast_win(update, context):
    """معالجة فوز الزر السريع"""
    query = update.callback_query
    user_id = str(query.from_user.id)

    if "fast_won" not in context.bot_data:
        context.bot_data["fast_won"] = True
        add_points(user_id, FAST_WIN_POINTS)
        update_stats("total_events", get_stats()["total_events"] + 1)

        await query.answer("🎉 مبروك! كنت الأسرع وربحت 100 نقطة!", show_alert=True)
        await query.edit_message_text(
            f"✅ **انتهت الفعالية!**\n\n"
            f"🏆 الفائز: {query.from_user.first_name}\n"
            f"💰 الجائزة: {FAST_WIN_POINTS} نقطة",
            parse_mode="Markdown"
        )

        # إعادة تعيين بعد دقيقة
        await asyncio.sleep(60)
        context.bot_data.pop("fast_won", None)
    else:
        await query.answer("😔 للأسف، شخص آخر كان أسرع منك!", show_alert=True)

async def handle_question_answer(update, context):
    """معالجة إجابة السؤال"""
    user = update.effective_user
    user_id = str(user.id)
    answer = update.message.text.lower().strip()

    for key, correct_answer in context.bot_data.items():
        if key.startswith("q_") and answer == correct_answer.lower():
            chat_id = key[2:]
            add_points(user_id, QUESTION_WIN_POINTS)
            update_stats("total_events", get_stats()["total_events"] + 1)

            await update.message.reply_text(
                f"🎉 إجابة صحيحة يا {user.first_name}!\n"
                f"ربحت {QUESTION_WIN_POINTS} نقطة!",
                parse_mode="Markdown"
            )
            context.bot_data.pop(key, None)
            return

from database.db_manager import get_stats