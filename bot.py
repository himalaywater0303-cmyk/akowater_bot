import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "8427218470:AAF9_sdfcFOJQcq5n34tkpKcMhh8Lxd5JXc"
GROUP_ID = -1003852199617  # Guruh ID ni yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# ====== HOLATLAR ======
class OrderState(StatesGroup):
    name = State()
    product = State()
    quantity = State()
    location = State()
    phone = State()


# ====== START ======
@dp.message_handler(commands='start')
async def start_handler(message: types.Message):
    await message.answer("Assalomu alaykum! Ismingizni kiriting:")
    await OrderState.name.set()


# ====== ISM ======
@dp.message_handler(state=OrderState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("5L - 6000 so'm")
    keyboard.add("10L - 8000 so'm")
    keyboard.add("18.9L - 15000 so'm")

    await message.answer("Qaysi mahsulotni tanlaysiz?", reply_markup=keyboard)
    await OrderState.product.set()


# ====== MAHSULOT ======
@dp.message_handler(state=OrderState.product)
async def get_product(message: types.Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer("Nechta kerak?")
    await OrderState.quantity.set()


# ====== SONI ======
@dp.message_handler(state=OrderState.quantity)
async def get_quantity(message: types.Message, state: FSMContext):
    await state.update_data(quantity=message.text)
    await message.answer("Manzilingizni kiriting:")
    await OrderState.location.set()


# ====== MANZIL ======
@dp.message_handler(state=OrderState.location)
async def get_location(message: types.Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Telefon raqamingizni kiriting:")
    await OrderState.phone.set()


# ====== TELEFON ======
@dp.message_handler(state=OrderState.phone)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    order_text = f"""
🚨 YANGI BUYURTMA

👤 Ism: {data['name']}
📦 Mahsulot: {data['product']}
🔢 Soni: {data['quantity']}
📍 Manzil: {data['location']}
📞 Tel: {data['phone']}
"""

    # Guruhga yuborish
    await bot.send_message(GROUP_ID, order_text)

    await message.answer("✅ Buyurtmangiz qabul qilindi!", reply_markup=types.ReplyKeyboardRemove())

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
