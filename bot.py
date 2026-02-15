import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("8427218470:AAF9_sdfcFOJQcq5n34tkpKcMhh8Lxd5JXc")
GROUP_ID = int(os.getenv("-1003852199617"))
ADMIN_ID = int(os.getenv("1028958055"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

order_counter = 1


class OrderState(StatesGroup):
    name = State()
    product = State()
    quantity = State()
    location = State()
    phone = State()


@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💧 Buyurtma berish")
    keyboard.add("📊 Statistika")

    await message.answer(
        "Assalomu alaykum!\nAKO Water buyurtma botiga xush kelibsiz 💧",
        reply_markup=keyboard
    )


@dp.message_handler(lambda message: message.text == "💧 Buyurtma berish")
async def order_start(message: types.Message):
    await message.answer("Ismingizni kiriting:")
    await OrderState.name.set()


@dp.message_handler(state=OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("5L - 6000 so'm")
    keyboard.add("10L - 8000 so'm")
    keyboard.add("18.9L - 15000 so'm")

    await message.answer("Mahsulotni tanlang:", reply_markup=keyboard)
    await OrderState.product.set()


@dp.message_handler(state=OrderState.product)
async def get_product(message: types.Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer("Nechta kerak?")
    await OrderState.quantity.set()


@dp.message_handler(state=OrderState.quantity)
async def get_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer("Manzilingizni kiriting:")
    await OrderState.location.set()


@dp.message_handler(state=OrderState.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Telefon raqamingizni kiriting:")
    await OrderState.phone.set()


@dp.message_handler(state=OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    global order_counter

    await state.update_data(phone=message.text)
    data = await state.get_data()

    order_id = f"#{order_counter:04d}"
    order_counter += 1

    order_text = f"""
🚨 YANGI BUYURTMA {order_id}

👤 Ism: {data['name']}
📦 Mahsulot: {data['product']}
🔢 Soni: {data['quantity']}
📍 Manzil: {data['location']}
📞 Tel: {data['phone']}
"""

    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Qabul qilindi", callback_data=f"confirm_{order_id}")
    )

    await bot.send_message(GROUP_ID, order_text, reply_markup=keyboard)

    await message.answer(f"✅ Buyurtmangiz qabul qilindi!\nBuyurtma raqami: {order_id}")

    await state.finish()


@dp.callback_query_handler(lambda c: c.data.startswith("confirm_"))
async def confirm_order(callback_query: types.CallbackQuery):
    order_id = callback_query.data.split("_")[1]

    await callback_query.answer("Buyurtma tasdiqlandi")
    await bot.send_message(
        ADMIN_ID,
        f"{order_id} buyurtma qabul qilindi ✅"
    )


@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def stats(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"Jami buyurtmalar soni: {order_counter - 1}")
    else:
        await message.answer("❌ Sizda ruxsat yo'q.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
