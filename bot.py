import telebot
from telebot import types

TOKEN = "8427218470:AAFNC81mmMl8d0op2xJzS7I8Vg5vOC8vPbo"
ADMIN_ID = 1028958055

bot = telebot.TeleBot(TOKEN)

user_data = {}

# START
@bot.message_handler(commands=['start'])
def start(message):
    user_data[message.chat.id] = {}
    bot.send_message(message.chat.id,
                     "Assalomu aleykum 👋\n\nAkowater_bot ga xush kelibsiz.\n\n1️⃣ Ism familiyangizni yozing:")
    bot.register_next_step_handler(message, get_name)


# 1️⃣ ISM
def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📞 Raqam yuborish", request_contact=True)
    markup.add(button)

    bot.send_message(message.chat.id,
                     "2️⃣ Telefon raqamingizni yuboring:",
                     reply_markup=markup)


# 2️⃣ TELEFON
@bot.message_handler(content_types=['contact'])
def get_phone(message):
    user_data[message.chat.id]['phone'] = message.contact.phone_number

    bot.send_message(message.chat.id,
                     "3️⃣ Manzilingizni yozing (Navoiy shahar):",
                     reply_markup=types.ReplyKeyboardRemove())

    bot.register_next_step_handler(message, get_address)


# 3️⃣ MANZIL
def get_address(message):
    user_data[message.chat.id]['address'] = message.text

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("5L – 6 000 so'm")
    markup.add("10L – 8 000 so'm")
    markup.add("18.9L – 15 000 so'm")

    bot.send_message(message.chat.id,
                     "4️⃣ Qaysi mahsulotimizni tanlaysiz?",
                     reply_markup=markup)


# 4️⃣ MAHSULOT
@bot.message_handler(func=lambda message: "L" in message.text)
def get_product(message):
    user_data[message.chat.id]['product'] = message.text

    bot.send_message(message.chat.id,
                     "5️⃣ Nechta buyurtma qilmoqchisiz?")
    bot.register_next_step_handler(message, get_quantity)


# 5️⃣ SONI
def get_quantity(message):
    user_data[message.chat.id]['quantity'] = message.text

    price_list = {
        "5L – 6 000 so'm": 6000,
        "10L – 8 000 so'm": 8000,
        "18.9L – 15 000 so'm": 15000
    }

    product = user_data[message.chat.id]['product']
    quantity = int(message.text)

    total = price_list[product] * quantity
    user_data[message.chat.id]['total'] = total

    text = f"""
📦 Yangi buyurtma!

👤 Ism: {user_data[message.chat.id]['name']}
📞 Telefon: {user_data[message.chat.id]['phone']}
📍 Manzil: {user_data[message.chat.id]['address']}

💧 Mahsulot: {product}
🔢 Soni: {quantity}
💰 Jami: {total} so'm
"""

    bot.send_message(ADMIN_ID, text)

    bot.send_message(message.chat.id,
                     f"6️⃣ Hisob-kitob:\n\n💰 Jami summa: {total} so'm\n\n🚚 Yetkazib berish bepul\n♻ Tara depozit yo'q")

    bot.send_message(message.chat.id,
                     "7️⃣ ✅ Buyurtmangiz qabul qilindi!\nTez orada siz bilan bog'lanamiz.",
                     reply_markup=types.ReplyKeyboardRemove())


print("Bot ishga tushdi...")
bot.infinity_polling()
