import telebot
from telebot import types
import sqlite3
import re
from datetime import datetime
import random

# ================== SOZLAMALAR ==================
TOKEN = "8427218470:AAF9_sdfcFOJQcq5n34tkpKcMhh8Lxd5JXc"
GROUP_ID = -1003852199617
ADMIN_ID = 1028958055
# ================================================

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE =====================
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
    order_id INTEGER,
    user_id INTEGER,
    product TEXT,
    quantity INTEGER,
    price INTEGER,
    address TEXT,
    status TEXT
)
""")

conn.commit()

# ================= MAHSULOTLAR ==================
products = {
    "💧 19L Suv": 25000,
    "💧 10L Suv": 15000,
    "💧 5L Suv": 6000
}

user_data = {}

# ================= START ========================
@bot.message_handler(commands=['start'])
def start(message):
    cursor.execute("SELECT * FROM users WHERE user_id=?",
                   (message.from_user.id,))
    user = cursor.fetchone()

    if user:
        send_menu(message)
    else:
        bot.send_message(message.chat.id,
                         "Assalamu aleykum akowater buyurtma botiga xush kelibsiz\n\nIsmingizni kiriting:")
        bot.register_next_step_handler(message, get_name)

# ================= ISM ==========================
def get_name(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "Raqamingizni kiriting:")
    bot.register_next_step_handler(message, get_phone)

# ================= TELEFON VALIDATION ===========
def get_phone(message):
    phone = message.text.strip()

    if not re.match(r'^\d{7,15}$', phone):
        bot.send_message(message.chat.id,
                         "❗ Raqamni to‘g‘ri kiriting (faqat son).")
        bot.register_next_step_handler(message, get_phone)
        return

    cursor.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
                   (message.from_user.id,
                    user_data[message.chat.id]["name"],
                    phone))
    conn.commit()

    send_menu(message)

# ================= MENU =========================
def send_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for product in products:
        markup.add(product)

    bot.send_message(message.chat.id,
                     "Menyu: qaysi mahsulotimizga buyurtma bermoqchisiz?",
                     reply_markup=markup)

# ================= MAHSULOT TANLASH =============
@bot.message_handler(func=lambda message: message.text in products)
def get_quantity(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]["product"] = message.text

    bot.send_message(message.chat.id, "Nechta?")
    bot.register_next_step_handler(message, calculate_price)

# ================= SON ==========================
def calculate_price(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id,
                         "❗ Iltimos son kiriting.")
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

# ================= YAKUN ========================
def finish_order(message):
    address = message.text
    order_id = random.randint(10000, 99999)

    cursor.execute("SELECT name, phone FROM users WHERE user_id=?",
                   (message.from_user.id,))
    user = cursor.fetchone()

    cursor.execute("""
    INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (order_id,
          message.from_user.id,
          user_data[message.chat.id]["product"],
          user_data[message.chat.id]["quantity"],
          user_data[message.chat.id]["price"],
          address,
          "Yangi"))

    conn.commit()

    group_text = f"""
🆕 YANGI BUYURTMA #{order_id}

👤 Ism: {user[0]}
📞 Telefon: {user[1]}

🛒 Mahsulot: {user_data[message.chat.id]['product']}
📦 Soni: {user_data[message.chat.id]['quantity']}
💰 Narxi: {user_data[message.chat.id]['price']:,} so‘m

📍 Manzil: {address}

⏰ {datetime.now().strftime("%d-%m-%Y %H:%M")}
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("✅ Qabul qilindi",
                                   callback_data=f"accept_{order_id}"),
        types.InlineKeyboardButton("❌ Bekor qilindi",
                                   callback_data=f"cancel_{order_id}")
    )

    bot.send_message(GROUP_ID, group_text, reply_markup=markup)

    bot.send_message(message.chat.id,
                     "✅ Buyurtmangiz qabul qilindi.\nOperatorlarimiz tez orada siz bilan bog‘lanishadi.")

    send_menu(message)

# ================= CALLBACK =====================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Faqat admin!")
        return

    action, order_id = call.data.split("_")

    if action == "accept":
        status = "Qabul qilindi"
    else:
        status = "Bekor qilindi"

    cursor.execute("UPDATE orders SET status=? WHERE order_id=?",
                   (status, order_id))
    conn.commit()

    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=None)

    bot.send_message(call.message.chat.id,
                     f"📦 Buyurtma #{order_id} — {status}")

# ================= ADMIN PANEL ==================
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM orders ORDER BY rowid DESC LIMIT 10")
    orders = cursor.fetchall()

    text = "📊 Oxirgi 10 ta buyurtma:\n\n"

    for order in orders:
        text += f"#{order[0]} | {order[2]} | {order[6]}\n"

    bot.send_message(message.chat.id, text)

# ================= RUN ==========================
bot.polling()
