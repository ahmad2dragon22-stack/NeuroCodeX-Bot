from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import main_menu_keyboard, back_button
from database.db_manager import get_user, get_stats
from utils.helpers import format_number, calculate_level
from config.settings import ADMIN_ID, DEVELOPER, VERSION
from features.events.events import handle_fast_win
from features.store.store import show_store, buy_item, add_item_start
from features.referral.referral import show_referral
from features.transfer.transfer import transfer_start
from admin.admin_panel import show_admin_panel

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج أمر البدء"""
    user = update.effective_user
    u_data = get_user(user.id, user.username)

    # معالجة الإحالة
    if context.args:
        from features.referral.referral import process_referral
        await process_referral(update, context, context.args[0])

    welcome_text = (
        f"👋 **أهلاً بك في Dragon Bot V{VERSION}**\n\n"
        f"🐉 منصتك المتكاملة للمسابقات والفعاليات!\n\n"
        f"🎯 **المميزات:**\n"
        f"• فعاليات يومية مثيرة\n"
        f"• متجر شامل للبيع والشراء\n"
        f"• نظام إحالة مجزي\n"
        f"• ألعاب وتحديات متنوعة\n\n"
        f"👤 المطور: {DEVELOPER}\n"
        f"⭐ ابدأ رحلتك الآن!"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=main_menu_keyboard(), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأزرار الرئيسي"""
    query = update.callback_query
    data = query.data
    user_id = str(query.from_user.id)

    if data == "balance":
        u = get_user(user_id)
        level = calculate_level(u["points"])
        await query.answer(
            f"💰 رصيدك: {format_number(u['points'])} نقطة\n🏆 مستواك: {level}",
            show_alert=True
        )

    elif data == "about":
        text = (
            "🐉 **Dragon Bot V2.0**\n\n"
            "🚀 **البوت الأكثر تطوراً للمسابقات!**\n\n"
            "✨ **المميزات الجديدة:**\n"
            "• نظام نقاط محسن\n"
            "• فعاليات تلقائية متقدمة\n"
            "• لوحة تحكم إدارية\n"
            "• ألعاب تفاعلية\n"
            "• واجهات محسنة\n\n"
            f"👨‍💻 المطور: {DEVELOPER}\n"
            f"📞 الدعم: @DragonSupport\n\n"
            "⚡ استمتع بالتجربة!"
        )
        await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

    elif data == "home":
        await start(update, context)

    elif data == "stats":
        from features.stats.stats import get_user_stats, get_global_stats, get_leaderboard
        user_stats = get_user_stats(user_id)
        global_stats = get_global_stats()
        leaderboard = get_leaderboard(5)

        text = (
            "📊 **إحصائياتك المتقدمة**\n\n"
            f"💰 النقاط: {format_number(user_stats['points'])}\n"
            f"🏆 المستوى: {user_stats['level']}\n"
            f"📈 التقدم: {user_stats['progress_percent']:.1f}%\n"
            f"🔗 الإحالات: {user_stats['referrals']}\n"
            f"🛒 المبيعات: {user_stats['items_sold']}\n"
            f"📅 أيام الانضمام: {user_stats['joined_days']}\n"
            f"📊 متوسط يومي: {user_stats['daily_avg']}\n\n"
            "🌍 **الإحصائيات العامة**\n"
            f"👥 المستخدمون: {format_number(global_stats['total_users'])}\n"
            f"🎯 الفعاليات: {format_number(global_stats['total_events'])}\n"
            f"💸 التحويلات: {format_number(global_stats['total_transfers'])}\n"
            f"💰 إجمالي النقاط: {format_number(global_stats['total_points'])}\n"
            f"🔥 النشطون: {global_stats['active_users']}\n\n"
            "🏅 **أفضل 5 مستخدمين**\n"
        )

        for i, user in enumerate(leaderboard[:5], 1):
            medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][i-1] if i <= 3 else f"{i}."
            text += f"{medal} {user['username'][:15]} - {format_number(user['points'])}\n"

        await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

    elif data == "events":
        text = (
            "🏆 **الفعاليات والمسابقات**\n\n"
            "🎪 **الفعاليات المتاحة:**\n"
            "• ⚡ تحدي السرعة\n"
            "• ❓ أسئلة سريعة\n"
            "• 🔗 مشاركة الروابط\n"
            "• 🎮 ألعاب مصغرة\n\n"
            "⏰ الفعاليات تُنشر تلقائياً!\n"
            "🏅 الفائزون يحصلون على نقاط إضافية!"
        )
        await query.edit_message_text(text, reply_markup=back_button(), parse_mode="Markdown")

    elif data == "games":
        from features.games.games import show_games_menu
        await show_games_menu(update, context)

    elif data == "game_guess":
        from features.games.games import start_guess_game
        await start_guess_game(update, context)

    elif data.startswith("guess_"):
        if data == "games":
            from features.games.games import show_games_menu
            await show_games_menu(update, context)
        else:
            guess_num = int(data.split("_")[1])
            from features.games.games import handle_guess
            await handle_guess(update, context, guess_num)

    elif data == "game_puzzle":
        from features.games.games import start_puzzle_game
        await start_puzzle_game(update, context)

    elif data == "game_speed":
        from features.games.games import start_speed_challenge
        await start_speed_challenge(update, context)

    elif data == "speed_ready":
        from features.games.games import handle_speed_ready
        await handle_speed_ready(update, context)

    elif data == "speed_click":
        from features.games.games import handle_speed_click
        await handle_speed_click(update, context)

    elif data.startswith("store_"):
        mode = data.split("_")[1]
        await show_store(update, context, mode)

    elif data.startswith("buy_"):
        parts = data.split("_")
        mode = parts[1]
        idx = int(parts[2])
        await buy_item(update, context, mode, idx)

    elif data == "add_item":
        await add_item_start(update, context)

    elif data == "referral":
        await show_referral(update, context)

    elif data == "transfer":
        await transfer_start(update, context)

    elif data == "win_fast":
        await handle_fast_win(update, context)

    elif data.startswith("admin"):
        if query.from_user.id == ADMIN_ID:
            if data == "admin":
                await show_admin_panel(update, context)
            elif data == "admin_stats":
                from admin.admin_panel import admin_stats
                await admin_stats(update, context)
            elif data == "admin_add_points":
                from admin.admin_panel import admin_add_points_start
                await admin_add_points_start(update, context)
            elif data == "admin_broadcast":
                from admin.admin_panel import admin_broadcast_start
                await admin_broadcast_start(update, context)
        else:
            await query.answer("❌ غير مصرح لك!", show_alert=True)

    else:
        await query.answer("🔄 جاري التطوير...", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالج الرسائل العامة"""
    await message_handler(update, context)
    """معالج الرسائل العامة"""
    user_data = context.user_data

    if "adding_item" in user_data:
        from features.store.store import add_item_name, add_item_price
        if "step" not in user_data:
            await add_item_name(update, context)
        elif user_data["step"] == "price":
            await add_item_price(update, context)

    elif user_data.get("admin_action") == "add_points":
        from admin.admin_panel import admin_add_points_id, admin_add_points_amount
        if "step" not in user_data:
            await admin_add_points_id(update, context)
        elif user_data["step"] == "amount":
            await admin_add_points_amount(update, context)

    elif user_data.get("admin_action") == "broadcast":
        from admin.admin_panel import admin_broadcast_send
        await admin_broadcast_send(update, context)

    # معالجة إجابات الألغاز
    from features.games.games import check_puzzle_answer
    await check_puzzle_answer(update, context)

    # معالجة إجابات الأسئلة
    from features.events.events import handle_question_answer
    await handle_question_answer(update, context)