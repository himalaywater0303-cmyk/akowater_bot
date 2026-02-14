import telebot
from telebot import types

TOKEN = "8427218470:AAFNC81mmMl8d0op2xJzS7I8Vg5vOC8vPbo"
ADMIN_ID = 1028958055

bot = telebot.TeleBot(TOKEN)

users = {}

prices = {
    "5L": 6000,
    "10L": 8000,
    "18.9L": 15000
}

# START
@bot.message_handler(commands=['start'])
def start(message):
    users[message.chat.id] = {"step": "name"}
    bot.send_message(message.chat.id,
                     "Assalomu aleykum 👋\n\nAkowater_bot ga xush kelibsiz.\n\n1️⃣ Ism familiyangizni yozing:")


@bot.message_handler(content_types=['text', 'contact'])
def handler(message):
    chat_id = message.chat.id

    if chat_id not in users:
        return

    step = users[chat_id]["step"]

    # 1️⃣ ISM
    if step == "name":
        users[chat_id]["name"] = message.text
        users[chat_id]["step"] = "phone"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn = types.KeyboardButton("📞 Raqam yuborish", request_contact=True)
        markup.add(btn)

        bot.send_message(chat_id,
                         "2️⃣ Telefon raqamingizni yuboring:",
                         reply_markup=markup)

    # 2️⃣ TELEFON
    elif step == "phone" and message.content_type == "contact":
        users[chat_id]["phone"] = message.contact.phone_number
        users[chat_id]["step"] = "address"

        bot.send_message(chat_id,
                         "3️⃣ Manzilingizni yozing (Navoiy shahar):",
                         reply_markup=types.ReplyKeyboardRemove())

    # 3️⃣ MANZIL
    elif step == "address":
        users[chat_id]["address"] = message.text
        users[chat_id]["step"] = "product"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("5L – 6 000 so'm")
        markup.add("10L – 8 000 so'm")
        markup.add("18.9L – 15 000 so'm")

        bot.send_message(chat_id,
                         "4️⃣ Qaysi mahsulotni tanlaysiz?",
                         reply_markup=markup)

    # 4️⃣ MAHSULOT
    elif step == "product":
        if "5L" in message.text:
            users[chat_id]["product"] = "5L"
        elif "10L" in message.text:
            users[chat_id]["product"] = "10L"
        elif "18.9L" in message.text:
            users[chat_id]["product"] = "18.9L"
        else:
            return

        users[chat_id]["step"] = "quantity"

        bot.send_message(chat_id,
                         "5️⃣ Nechta buyurtma qilmoqchisiz?")

    # 5️⃣ SONI
    elif step == "quantity":
        try:
            qty = int(message.text)
        except:
            bot.send_message(chat_id, "Iltimos faqat raqam yozing.")
            return

        users[chat_id]["quantity"] = qty
        product = users[chat_id]["product"]
        total = prices[product] * qty
        users[chat_id]["total"] = total

        text = f"""
📦 YANGI BUYURTMA

👤 Ism: {users[chat_id]['name']}
📞 Telefon: {users[chat_id]['phone']}
📍 Manzil: {users[chat_id]['address']}

💧 Mahsulot: {product}
🔢 Soni: {qty}
💰 Jami: {total} so'm
"""

        bot.send_message(ADMIN_ID, text)

        bot.send_message(chat_id,
                         f"6️⃣ Hisob:\n\n💰 Jami summa: {total} so'm\n🚚 Yetkazib berish bepul\n♻ Tara depozit yo'q")

        bot.send_message(chat_id,
                         "7️⃣ ✅ Buyurtmangiz qabul qilindi!\nTez orada bog'lanamiz.",
                         reply_markup=types.ReplyKeyboardRemove())

        users.pop(chat_id)

print("Bot ishga tushdi...")
bot.infinity_polling()

from telegram.ext import CommandHandler

async def show_id(update, context):
    await update.message.reply_text(str(update.effective_chat.id))

application.add_handler(CommandHandler("id", show_id))
