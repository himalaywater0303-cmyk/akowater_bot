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

# ================= DATA =================

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "orders": 0}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

# ================= MENUS =================

def main_menu(is_admin=False):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("💧 Buyurtma berish"))
    if is_admin:
        kb.add(KeyboardButton("📊 Statistika"))
    return kb

def phone_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📞 Raqamni yuborish", request_contact=True))
    return kb

def location_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("📍 Joylashuvni yuborish", request_location=True))
    return kb

# ================= START =================

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = str(message.from_user.id)

    if user_id not in data["users"]:
        data["users"][user_id] = {"step": "name"}
        save_data(data)
        await message.answer("Ismingizni kiriting:")
        return

    await message.answer(
        "Assalomu alaykum 💧",
        reply_markup=main_menu(int(user_id) == ADMIN_ID)
    )

# ================= MAIN HANDLER =================

@dp.message_handler(content_types=types.ContentTypes.ANY)
async def handler(message: types.Message):

    user_id = str(message.from_user.id)

    if user_id not in data["users"]:
        await message.answer("Iltimos /start bosing.")
        return

    user = data["users"][user_id]
    step = user.get("step", "menu")

    # ===== ADMIN STATISTIKA =====
    if message.text == "📊 Statistika" and int(user_id) == ADMIN_ID:
        await message.answer(
            f"📊 Statistika\n\n👥 Users: {len(data['users'])}\n📦 Orders: {data['orders']}"
        )
        return

    # ===== REGISTRATION =====
    if step == "name":
        if len(message.text) < 2:
            await message.answer("Ismni to‘g‘ri kiriting.")
            return

        user["name"] = message.text
        user["step"] = "menu"
        save_data(data)

        await message.answer(
            "Ro'yxatdan o'tdingiz ✅",
            reply_markup=main_menu(int(user_id) == ADMIN_ID)
        )
        return

    # ===== ORDER START =====
    if message.text == "💧 Buyurtma berish":

        if step != "menu":
            await message.answer("⚠️ Avvalgi buyurtmani tugating.")
            return

        user["step"] = "quantity"
        save_data(data)
        await message.answer("Nechta kerak?")
        return

    # ===== QUANTITY =====
    if step == "quantity":
        if not message.text.isdigit():
            await message.answer("Iltimos son kiriting.")
            return

        user["quantity"] = message.text
        user["step"] = "location"
        save_data(data)

        await message.answer(
            "Joylashuvni yuboring:",
            reply_markup=location_keyboard()
        )
        return

    # ===== LOCATION =====
    if step == "location":

        if message.location:
            lat = message.location.latitude
            lon = message.location.longitude
            user["location"] = f"https://maps.google.com/?q={lat},{lon}"
            user["step"] = "phone"
            save_data(data)

            await message.answer(
                "Telefon raqamingizni yuboring:",
                reply_markup=phone_keyboard()
            )
            return

        await message.answer("Iltimos 📍 tugma orqali joylashuv yuboring.")
        return

    # ===== PHONE =====
    if step == "phone":

        if message.contact:
            user["phone"] = message.contact.phone_number
        else:
            await message.answer("Iltimos 📞 tugma orqali raqam yuboring.")
            return

        user["step"] = "menu"
        data["orders"] += 1
        order_number = data["orders"]
        save_data(data)

        order_text = (
            f"🆕 Yangi buyurtma #{order_number}\n\n"
            f"👤 Ism: {user['name']}\n"
            f"📦 Soni: {user['quantity']}\n"
            f"📍 Lokatsiya: {user['location']}\n"
            f"📞 Telefon: {user['phone']}"
        )

        await bot.send_message(GROUP_ID, order_text)

        await message.answer(
            f"✅ Buyurtmangiz qabul qilindi!\nBuyurtma raqami: #{order_number}",
            reply_markup=main_menu(int(user_id) == ADMIN_ID)
        )
        return

# ================= RUN =================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
