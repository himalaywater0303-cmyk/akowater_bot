import telebot
from telebot import types

TOKEN = "8427218470:AAFNC81mmMl8d0op2xJzS7I8Vg5vOC8vPbo"
ADMIN_ID = 1028958055

bot = telebot.TeleBot(TOKEN)

users = {}

prices = {
    "5 litr": 5000,
    "10 litr": 10000,
    "18.9 litr": 15000
}

@bot.message_handler(commands=['start'])
def start(message):
    users[message.chat.id] = {}
    bot.send_message(message.chat.id,
                     "Assalomu aleykum 👋\n\nAkowater_bot ga xush kelibsiz.\n\n1️⃣ Ism familiyangizni yozing:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    users[message.chat.id]['name'] = message.text
    bot.send_message(message.chat.id, "2️⃣ Telefon raqamingizni yozing:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    users[message.chat.id]['phone'] = message.text
    bot.send_message(message.chat.id, "3️⃣ Manzilingizni yozing (faqat Navoiy shahar):")
    bot.register_next_step_handler(message, get_address)

def get_address(message):
    if "navoiy" not in message.text.lower():
        bot.send_message(message.chat.id, "❌ Biz faqat Navoiy shahar ichida yetkazib beramiz.")
        return

    users[message.chat.id]['address'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for product in prices.keys():
        markup.add(product)

    bot.send_message(message.chat.id, "4️⃣ Qaysi mahsulotimizni tanlaysiz?", reply_markup=markup)
    bot.register_next_step_handler(message, get_product)

def get_product(message):
    if message.text not in prices:
        bot.send_message(message.chat.id, "❌ Tugmalardan birini tanlang.")
        return

    users[message.chat.id]['product'] = message.text
    users[message.chat.id]['price'] = prices[message.text]

    bot.send_message(message.chat.id, "5️⃣ Nechta dona olmoqchisiz?")
    bot.register_next_step_handler(message, get_quantity)

def get_quantity(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❌ Faqat son kiriting.")
        return

    quantity = int(message.text)
    users[message.chat.id]['quantity'] = quantity

    total = quantity * users[message.chat.id]['price']
    users[message.chat.id]['total'] = total

    bot.send_message(message.chat.id,
                     f"6️⃣ Umumiy hisob: {total} so'm\n\nTasdiqlaysizmi? (ha/yo'q)")
    bot.register_next_step_handler(message, confirm_order)

def confirm_order(message):
    if message.text.lower() != "ha":
        bot.send_message(message.chat.id, "❌ Buyurtma bekor qilindi.")
        return

    data = users[message.chat.id]

    text = f"""
🛒 YANGI BUYURTMA

👤 Ism: {data['name']}
📞 Telefon: {data['phone']}
📍 Manzil: {data['address']}
💧 Mahsulot: {data['product']}
🔢 Soni: {data['quantity']}
💰 Jami: {data['total']} so'm
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Qabul qilish", callback_data=f"accept_{message.chat.id}"),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_{message.chat.id}")
    )

    bot.send_message(ADMIN_ID, text, reply_markup=markup)
    bot.send_message(message.chat.id, "7️⃣ ✅ Buyurtmangiz qabul qilindi! Tez orada bog'lanamiz.")

    del users[message.chat.id]

@bot.callback_query_handler(func=lambda call: True)
def admin_actions(call):
    user_id = int(call.data.split("_")[1])

    if call.data.startswith("accept"):
        bot.send_message(user_id, "✅ Buyurtmangiz tasdiqlandi. Yetkazib beriladi.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    elif call.data.startswith("cancel"):
        bot.send_message(user_id, "❌ Buyurtmangiz bekor qilindi.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

bot.polling(none_stop=True)
