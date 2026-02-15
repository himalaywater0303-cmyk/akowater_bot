import telebot
from telebot import types
import sqlite3
import re
from datetime import datetime
import random

TOKEN = "BOT_TOKENINGIZNI_QOYING"
GROUP_ID = -100XXXXXXXXXX  # gruppa id

bot = telebot.TeleBot(TOKEN)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT
)
""")

conn.commit()

# ---------------- MAHSULOTLAR ----------------
products = {
    "💧 19L Suv": 25000,
    "💧 10L Suv": 15000,
    "💧 5L Suv": 6000
}

user_data = {}

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        send_menu(message)
    else:
        bot.send_message(message.chat.id,
                         "Assalamu aleykum akowater buyurtma botiga xush kelibsiz\n\nIsmingizni kiriting:")
        bot.register_next_step_handler(message, get_name)

# ---------------- NAME ----------------
def get_name(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "Raqamingizni kiriting:")
    bot.register_next_step_handler(message, get_phone)

# ---------------- PHONE VALIDATION ----------------
def get_phone(message):
    phone = message.text.strip()

    if not re.match(r'^\d{7,15}$', phone):
        bot.send_message(message.chat.id, "❗ Raqamni to‘g‘ri kiriting (faqat son).")
        bot.register_next_step_handler(message, get_phone)
        return

    user_data[message.chat.id]["phone"] = phone

    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                   (message.from_user.id,
                    user_data[message.chat.id]["name"],
                    phone))
    conn.commit()

    send_menu(message)

# ---------------- MENU ----------------
def send_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for product in products:
        markup.add(product)

    bot.send_message(message.chat.id,
                     "Menyu: qaysi mahsulotimizga buyurtma bermoqchisiz?",
                     reply_markup=markup)

# ---------------- PRODUCT ----------------
@bot.message_handler(func=lambda message: message.text in products)
def get_quantity(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]["product"] = message.text

    bot.send_message(message.chat.id, "Nechta?")
    bot.register_next_step_handler(message, calculate_price)

# ---------------- QUANTITY ----------------
def calculate_price(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "❗ Iltimos son kiriting.")
        bot.register_next_step_handler(message, calculate_price)
        return

    quantity = int(message.text)
    product = user_data[message.chat.id]["product"]
    price = products[product] * quantity

    user_data[message.chat.id]["quantity"] = quantity
    user_data[message.chat.id]["price"] = price

    bot.send_message(message.chat.id,
                     f"Hisob narxi: {price:,} so‘m\n\nManzilingizni kiriting:")
    bot.register_next_step_handler(message, finish_order)

# ---------------- FINISH ----------------
def finish_order(message):
    address = message.text
    user_data[message.chat.id]["address"] = address

    order_id = random.randint(10000, 99999)

    # GROUPGA CHIROYLI FORMAT
    group_text = f"""
🆕 YANGI BUYURTMA #{order_id}

👤 Ism: {message.from_user.first_name}
📞 Telefon: {cursor.execute("SELECT phone FROM users WHERE user_id=?", (message.from_user.id,)).fetchone()[0]}

🛒 Mahsulot: {user_data[message.chat.id]['product']}
📦 Soni: {user_data[message.chat.id]['quantity']}
💰 Narxi: {user_data[message.chat.id]['price']:,} so‘m

📍 Manzil: {address}

⏰ Vaqt: {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Qabul qilindi", callback_data=f"accept_{order_id}"))

    bot.send_message(GROUP_ID, group_text, reply_markup=markup)

    bot.send_message(message.chat.id,
                     "✅ Buyurtmangiz qabul qilindi.\nOperatorlarimiz tez orada siz bilan bog‘lanishadi.")

    send_menu(message)

# ---------------- CALLBACK ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def accept_order(call):
    bot.answer_callback_query(call.id, "Buyurtma qabul qilindi!")

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=None)

    bot.send_message(call.message.chat.id,
                     f"✅ {call.data.split('_')[1]} buyurtma qabul qilindi.")

# ---------------- RUN ----------------
bot.polling()
