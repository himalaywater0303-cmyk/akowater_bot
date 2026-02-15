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

# ------------------ DATA LOAD ------------------

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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("💧 Buyurtma berish"))
    return keyboard

def admin_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("📊 Statistika"))
    keyboard.add(KeyboardButton("📦 Buyurtmalar soni"))
    return keyboard

# ------------------ START ------------------

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id not in data["users"]:
        await message.answer("Ismingizni kiriting:")
        data["users"][user_id] = {"step": "name"}
        save_data(data)
    else:
        if int(user_id) == ADMIN_ID:
            await message.answer("Admin panel 👑", reply_markup=admin_menu())
        else:
            await message.answer("Assalomu alaykum! 💧", reply_markup=user_menu())

# ------------------ MESSAGE HANDLER ------------------

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)

    # ADMIN PANEL
    if int(user_id) == ADMIN_ID:
        if message.text == "📊 Statistika":
            total_users = len(data["users"])
            total_orders = data["orders"]
            await message.answer(
                f"📊 Statistika\n\n👥 Foydalanuvchilar: {total_users}\n📦 Buyurtmalar: {total_orders}"
            )
            return

        if message.text == "📦 Buyurtmalar soni":
            await message.answer(f"📦 Jami buyurtmalar: {data['orders']}")
            return

    # REGISTRATION FLOW
    if user_id in data["users"] and data["users"][user_id].get("step") == "name":
        data["users"][user_id]["name"] = message.text
        data["users"][user_id]["step"] = "menu"
        save_data(data)
        await message.answer("Ro'yxatdan o'tdingiz ✅", reply_markup=user_menu())
        return

    # ORDER FLOW
    if message.text == "💧 Buyurtma berish":
        data["users"][user_id]["step"] = "quantity"
        save_data(data)
        await message.answer("Nechta kerak?")
        return

    if user_id in data["users"] and data["users"][user_id].get("step") == "quantity":
        data["users"][user_id]["quantity"] = message.text
        data["users"][user_id]["step"] = "address"
        save_data(data)
        await message.answer("Manzilingizni kiriting:")
        return

    if user_id in data["users"] and data["users"][user_id].get("step") == "address":
        data["users"][user_id]["address"] = message.text
        data["users"][user_id]["step"] = "phone"
        save_data(data)
        await message.answer("Telefon raqamingizni kiriting:")
        return

    if user_id in data["users"] and data["users"][user_id].get("step") == "phone":
        data["users"][user_id]["phone"] = message.text
        data["users"][user_id]["step"] = "menu"
        data["orders"] += 1

        order_number = data["orders"]
        save_data(data)

        user = data["users"][user_id]

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

# ------------------ RUN ------------------

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
