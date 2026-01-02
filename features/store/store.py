from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from database.db_manager import load_db, save_db, add_points
from keyboards.keyboards import store_keyboard, back_button
from utils.helpers import escape_markdown

async def show_store(update, context, mode):
    """عرض المتجر"""
    query = update.callback_query
    store_type = "الرسمي 🏢" if mode == "official" else "العام 🏪"
    db = load_db()
    items = db["official_store"] if mode == "official" else db["public_store"]

    text = f"🛒 **مرحباً بك في المتجر {store_type}**\n\n"
    if not items:
        text += "📭 لا توجد منتجات حالياً.\n\n💡 كن أول من يضيف منتجاً!"
    else:
        text += f"📦 عدد المنتجات: {len(items)}\n\n"

    can_add = mode == "public"
    keyboard = store_keyboard(items, mode, can_add)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def buy_item(update, context, mode, idx):
    """شراء منتج"""
    query = update.callback_query
    user_id = str(query.from_user.id)
    db = load_db()

    items = db["official_store"] if mode == "official" else db["public_store"]
    if idx >= len(items):
        await query.answer("❌ المنتج غير موجود!", show_alert=True)
        return

    item = items[idx]
    user = db["users"].get(user_id)
    if not user or user["points"] < item["price"]:
        await query.answer("❌ ليس لديك نقاط كافية!", show_alert=True)
        return

    # خصم النقاط
    user["points"] -= item["price"]
    seller_id = item.get("seller_id")
    if seller_id and seller_id != user_id:
        db["users"][seller_id]["points"] += item["price"]
        db["users"][seller_id]["items_sold"] += 1

    # إزالة المنتج من المتجر
    items.pop(idx)
    save_db(db)

    await query.answer("✅ تم الشراء بنجاح!", show_alert=True)
    await query.edit_message_text(
        f"🎉 **تم الشراء بنجاح!**\n\n"
        f"🛒 المنتج: {escape_markdown(item['name'])}\n"
        f"💰 السعر: {item['price']} نقطة\n\n"
        f"📨 سيتم تسليم المنتج قريباً!",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )

async def add_item_start(update, context):
    """بدء إضافة منتج"""
    query = update.callback_query
    context.user_data["adding_item"] = True
    await query.edit_message_text(
        "➕ **إضافة منتج جديد**\n\n"
        "أرسل اسم المنتج:",
        reply_markup=back_button(),
        parse_mode="Markdown"
    )

async def add_item_name(update, context):
    """تلقي اسم المنتج"""
    if "adding_item" not in context.user_data:
        return

    context.user_data["item_name"] = update.message.text
    context.user_data["step"] = "price"
    await update.message.reply_text(
        "💰 أرسل سعر المنتج (بالنقاط):",
        parse_mode="Markdown"
    )

async def add_item_price(update, context):
    """تلقي سعر المنتج"""
    if context.user_data.get("step") != "price":
        return

    valid, price = validate_amount(update.message.text)
    if not valid:
        await update.message.reply_text("❌ السعر يجب أن يكون رقماً صحيحاً!")
        return

    user_id = str(update.effective_user.id)
    db = load_db()

    item = {
        "name": context.user_data["item_name"],
        "price": price,
        "seller_id": user_id,
        "added_at": str(datetime.now())
    }

    db["public_store"].append(item)
    save_db(db)

    await update.message.reply_text(
        f"✅ **تم إضافة المنتج بنجاح!**\n\n"
        f"🛒 المنتج: {escape_markdown(item['name'])}\n"
        f"💰 السعر: {price} نقطة",
        parse_mode="Markdown"
    )

    context.user_data.clear()

from datetime import datetime
from utils.helpers import validate_amount