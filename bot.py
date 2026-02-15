import logging
import os
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "data.json"

# ------------------ DATA ------------------

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "orders": 0}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ------------------ MENUS ------------------

def user_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💧 Buyurtma berish"))
    return kb

def admin_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📊 Statistika"))
    kb.add(KeyboardButton("💧 Buyurtma berish"))
    return kb

# ------------------ START ------------------

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id not in data["users"]:
        data["users"][user_id] = {"step": "name"}
        save_data(data)
        await message.answer("Ismingizni kiriting:")
        return

    await show_menu(message, user_id)

async def show_menu(message, user_id):
    if int(user_id) == ADMIN_ID:
        await message.answer("Admin panel 👑", reply_markup=admin_menu())
    else:
        await message.answer("Assalomu alaykum! 💧", reply_markup=user_menu())

# ------------------ MAIN HANDLER ------------------

@dp.message_handler()
async def handler(message: types.Message):
    user_id = str(message.from_user.id)
    text = message.text

    # USER mavjudligini tekshirish
    if user_id not in data["users"]:
        await message.answer("Iltimos /start bosing.")
        return

    user = data["users"][user_id]
    step = user.get("step", "menu")

    # ---------------- ADMIN ----------------
    if int(user_id) == ADMIN_ID and text == "📊 Statistika":
        await message.answer(
            f"📊 Statistika\n\n👥 Users: {len(data['users'])}\n📦 Orders: {data['orders']}"
        )
        return

    # ---------------- REGISTRATION ----------------
    if step == "name":
        user["name"] = text
        user["step"] = "menu"
        save_data(data)
        await message.answer("Ro'yxatdan o'tdingiz ✅", reply_markup=user_menu())
        return

    # ---------------- ORDER START ----------------
    if text == "💧 Buyurtma berish":

        if step != "menu":
            await message.answer("⚠️ Avvalgi buyurtmani tugating.")
            return

        user["step"] = "quantity"
        save_data(data)
        await message.answer("Nechta kerak?")
        return

    # ---------------- QUANTITY ----------------
    if step == "quantity":
        if not text.isdigit():
            await message.answer("Iltimos son kiriting.")
            return

        user["quantity"] = text
        user["step"] = "address"
        save_data(data)
        await message.answer("Manzilingizni kiriting:")
        return

    # ---------------- ADDRESS ----------------
    if step == "address":
        user["address"] = text
        user["step"] = "phone"
        save_data(data)
        await message.answer("Telefon raqamingizni kiriting:")
        return

    # ---------------- PHONE ----------------
    if step == "phone":
        user["phone"] = text
        user["step"] = "menu"
        data["orders"] += 1
        order_number = data["orders"]
        save_data(data)

        order_text = (
            f"🆕 Yangi buyurtma #{order_number}\n\n"
            f"👤 Ism: {user['name']}\n"
            f"📦 Soni: {user['quantity']}\n"
            f"📍 Manzil: {user['address']}\n"
            f"📞 Telefon: {user['phone']}"
        )

        await bot.send_message(GROUP_ID, order_text)

        await message.answer(
            f"✅ Buyurtmangiz qabul qilindi!\nBuyurtma raqami: #{order_number}",
            reply_markup=user_menu()
        )
        return

# ---------------- RUN ----------------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
