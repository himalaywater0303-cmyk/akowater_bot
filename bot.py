import telebot
from telebot import types
import sqlite3
import os
from datetime import datetime
import re

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =================
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    phone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product TEXT,
    quantity INTEGER,
    total INTEGER,
    status TEXT,
    date TEXT
)
""")

conn.commit()

prices = {
    "5L": 6000,
    "10L": 8000,
    "18.9L": 15000
}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if user:
        bot.send_message(user_id, "💧 Qaytganingizdan xursandmiz!\nMahsulotni tanlang:")
        ask_product(message)
    else:
        bot.send_message(user_id,
                         "💧 Assalamu alaykum AKO Water buyurtma botiga xush kelibsiz.\n\nIsmingizni kiriting:")
        bot.register_next_step_handler(message, get_name)

# ================= RO‘YXAT =================
def get_name(message):
    name = message.text
    bot.send_message(message.chat.id, "📞 Raqamingizni kiriting:")
    bot.register_next_step_handler(message, lambda m: get_phone(m, name))

def get_phone(message, name):
    phone = message.text
    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                   (message.chat.id, name, phone))
    conn.commit()
    ask_product(message)

# ================= PRODUCT =================
def ask_product(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("5L", "10L", "18.9L")
    bot.send_message(message.chat.id, "💧 Mahsulotni tanlang:", reply_markup=markup)
    bot.register_next_step_handler(message, get_product)

def get_product(message):
    product = message.text
    if product not in prices:
        ask_product(message)
        return

    bot.send_message(message.chat.id, "Nechta kerak? (masalan: 2 yoki 2ta)")
    bot.register_next_step_handler(message, lambda m: get_quantity(m, product))

# ================= SON =================
def get_quantity(message, product):
    number = re.findall(r'\d+', message.text)
    if not number:
        bot.send_message(message.chat.id, "Iltimos son kiriting.")
        return

    quantity = int(number[0])
    total = prices[product] * quantity
    date = datetime.now().strftime("%d.%m.%Y %H:%M")

    cursor.execute("""
    INSERT INTO orders (user_id, product, quantity, total, status, date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (message.chat.id, product, quantity, total, "Yangi", date))
    conn.commit()

    order_id = cursor.lastrowid

    cursor.execute("SELECT name, phone FROM users WHERE user_id=?",
                   (message.chat.id,))
    user = cursor.fetchone()

    text = f"""
🆕 YANGI BUYURTMA #{order_id}

👤 {user[0]}
📞 {user[1]}
💧 {product}
📦 {quantity} ta
💰 {total:,} so'm
⏰ {date}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Qabul qilindi",
                                   callback_data=f"ok_{order_id}"),
        types.InlineKeyboardButton("❌ Bekor qilindi",
                                   callback_data=f"cancel_{order_id}")
    )

    bot.send_message(ADMIN_ID, text, reply_markup=markup)

    bot.send_message(message.chat.id,
                     f"💰 Jami hisob: {total:,} so'm\n\n"
                     "✅ Buyurtmangiz qabul qilindi.\n"
                     "Operatorlarimiz tez orada siz bilan bog'lanishadi.",
                     reply_markup=types.ReplyKeyboardRemove())

# ================= ADMIN BUTTON =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data.split("_")
    action = data[0]
    order_id = int(data[1])

    if action == "ok":
        cursor.execute("UPDATE orders SET status=? WHERE id=?",
                       ("Qabul qilindi", order_id))
        bot.answer_callback_query(call.id, "Buyurtma qabul qilindi")
    else:
        cursor.execute("UPDATE orders SET status=? WHERE id=?",
                       ("Bekor qilindi", order_id))
        bot.answer_callback_query(call.id, "Buyurtma bekor qilindi")

    conn.commit()

# ================= STATISTIKA =================
@bot.message_handler(commands=['stat'])
def stat(message):
    if message.chat.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM orders")
    total_orders = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM orders WHERE status='Qabul qilindi'")
    total_income = cursor.fetchone()[0] or 0

    bot.send_message(ADMIN_ID,
                     f"📊 STATISTIKA\n\n"
                     f"🛒 Jami buyurtmalar: {total_orders}\n"
                     f"💰 Jami tushum: {total_income:,} so'm")

# ================= RUN =================
if __name__ == "__main__":
    print("Bot ishga tushdi...")
    bot.polling(none_stop=True)
