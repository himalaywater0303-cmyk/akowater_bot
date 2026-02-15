import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("8427218470:AAFNC81mmMl8d0op2xJzS7I8Vg5vOC8vPbo")
ADMIN_ID = int(os.getenv("-1003852199617"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

prices = {
    "5L": 6000,
    "10L": 8000,
    "18.9L": 15000
}

user_cart = {}
user_data = {}

# MAIN MENU
def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💧 Mahsulotlar")
    kb.add("🛒 Savat")
    kb.add("☎️ Aloqa")
    return kb

# START
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📞 Telefon raqam yuborish", request_contact=True))
    
    await message.answer(
        "Assalomu alaykum!\n\nHurmatli mijoz 👋\nIltimos, telefon raqamingizni yuboring.",
        reply_markup=kb
    )

# CONTACT SAVE
@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_handler(message: types.Message):
    user_data[message.from_user.id] = {
        "phone": message.contact.phone_number,
        "username": message.from_user.username
    }
    
    await message.answer(
        "Rahmat ✅\n\nHurmatli mijoz, menyudan tanlang 👇",
        reply_markup=main_menu()
    )

# PRODUCTS
@dp.message_handler(lambda message: message.text == "💧 Mahsulotlar")
async def products(message: types.Message):
    markup = InlineKeyboardMarkup()
    for key, value in prices.items():
        markup.add(
            InlineKeyboardButton(
                text=f"{key} - {value} so'm",
                callback_data=f"add_{key}"
            )
        )
    await message.answer("💧 Mahsulotni tanlang:", reply_markup=markup)

# ADD TO CART
@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback_query: types.CallbackQuery):
    product = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    
    user_cart.setdefault(user_id, {})
    user_cart[user_id].setdefault(product, 0)
    user_cart[user_id][product] += 1
    
    await callback_query.answer("Savatga qo'shildi ✅")

# CART
@dp.message_handler(lambda message: message.text == "🛒 Savat")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_cart or not user_cart[user_id]:
        await message.answer("Savat bo'sh 🛒")
        return
    
    text = "🛒 Savatingiz:\n\n"
    total = 0
    
    for product, qty in user_cart[user_id].items():
        price = prices[product] * qty
        total += price
        text += f"{product} x{qty} = {price} so'm\n"
    
    text += f"\n💰 Jami: {total} so'm"
    
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📍 Manzil yuborish", request_location=True)
    kb.add("⬅️ Ortga")
    
    await message.answer(text, reply_markup=kb)

# LOCATION
@dp.message_handler(content_types=types.ContentType.LOCATION)
async def location_handler(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_cart:
        return
    
    latitude = message.location.latitude
    longitude = message.location.longitude
    
    text = "🆕 Yangi buyurtma!\n\n"
    total = 0
    
    for product, qty in user_cart[user_id].items():
        price = prices[product] * qty
        total += price
        text += f"{product} x{qty} = {price} so'm\n"
    
    text += f"\n💰 Jami: {total} so'm\n"
    text += f"\n📞 Telefon: {user_data[user_id]['phone']}"
    text += f"\n👤 Username: @{user_data[user_id]['username']}"
    text += f"\n📍 Manzil: https://maps.google.com/?q={latitude},{longitude}"
    
    await bot.send_message(ADMIN_ID, text)
    
    user_cart[user_id] = {}
    
    await message.answer("Hurmatli mijoz, buyurtmangiz qabul qilindi ✅", reply_markup=main_menu())

# CONTACT
@dp.message_handler(lambda message: message.text == "☎️ Aloqa")
async def contact(message: types.Message):
    await message.answer("📞 +998 XX XXX XX XX")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
