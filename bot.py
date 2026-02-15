import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ====== O'ZGARTIRING ======
BOT_TOKEN = "8427218470:AAF9_sdfcFOJQcq5n34tkpKcMhh8Lxd5JXc"
GROUP_ID = -1003852199617  # Guruh ID
# ===========================

logging.basicConfig(level=logging.INFO)

NAME, PRODUCT, QUANTITY, LOCATION, PHONE = range(5)

products = {
    "5L - 6000 so'm": "5L",
    "10L - 8000 so'm": "10L",
    "18.9L - 15000 so'm": "18.9L",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! Ismingizni kiriting:")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = [[p] for p in products.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Qaysi mahsulotni tanlaysiz?",
        reply_markup=reply_markup
    )
    return PRODUCT

async def get_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["product"] = update.message.text
    await update.message.reply_text("Nechta kerak?")
    return QUANTITY

async def get_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quantity"] = update.message.text
    await update.message.reply_text("Manzilingizni kiriting:")
    return LOCATION

async def get_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text
    await update.message.reply_text("Telefon raqamingizni kiriting:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text

    order_text = f"""
🚨 YANGI BUYURTMA

👤 Ism: {context.user_data['name']}
📦 Mahsulot: {context.user_data['product']}
🔢 Soni: {context.user_data['quantity']}
📍 Manzil: {context.user_data['location']}
📞 Tel: {context.user_data['phone']}
"""

    # Guruhga yuborish
    await context.bot.send_message(chat_id=GROUP_ID, text=order_text)

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Buyurtma bekor qilindi.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quantity)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_location)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
