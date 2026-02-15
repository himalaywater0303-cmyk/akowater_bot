import os
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from openpyxl import Workbook, load_workbook

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

users = {}
order_counter = 1

PRODUCTS = {
    "💧 19L Suv": 15000,
    "💧 10L Suv": 10000,
    "💧 5L Suv": 6000
}

PAYMENT_LINK = "https://your-click-or-payme-link"  # To‘lov link qo‘y


# ------------------ Excel ------------------

def save_to_excel(data):
    file = "orders.xlsx"
    try:
        wb = load_workbook(file)
        ws = wb.active
    except:
        wb = Workbook()
        ws = wb.active
        ws.append(["ID", "Ism", "Telefon", "Mahsulot",
                   "Soni", "Summa", "Manzil", "Sana"])

    ws.append([
        data["id"],
        data["name"],
        data["phone"],
        data["product"],
        data["quantity"],
        data["total"],
        data["address"],
        data["date"]
    ])
    wb.save(file)


# ------------------ Menyu ------------------

def product_menu():
    keyboard = [[KeyboardButton(text=name)] for name in PRODUCTS.keys()]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# ------------------ START ------------------

@dp.message(lambda m: m.text == "/start")
async def start(message: types.Message):
    user_id = message.from_user.id

    # Agar oldin ro‘yxatdan o‘tgan bo‘lsa
    if user_id in users and "name" in users[user_id] and "phone" in users[user_id]:
        users[user_id]["step"] = "product"
        await message.answer(
            "Qaysi mahsulotimizga buyurtma bermoqchisiz?",
            reply_markup=product_menu()
        )
        return

    users[user_id] = {"step": "name"}

    await message.answer(
        "Assalamu aleykum akowater buyurtma botiga xush kelibsiz 💧\n\nIsm:"
    )


# ------------------ ADMIN ------------------

@dp.message(lambda m: m.text == "/admin")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📊 Admin panel\n/orders - Excel faylni olish")


@dp.message(lambda m: m.text == "/orders")
async def send_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    if os.path.exists("orders.xlsx"):
        await message.answer_document(types.FSInputFile("orders.xlsx"))
    else:
        await message.answer("Hozircha buyurtmalar yo‘q.")


# ------------------ MAIN FLOW ------------------

@dp.message()
async def handler(message: types.Message):
    global order_counter

    user_id = message.from_user.id
    text = message.text

    if user_id not in users:
        await message.answer("Iltimos /start bosing.")
        return

    step = users[user_id]["step"]

    # 1️⃣ ISM
    if step == "name":
        if len(text) < 2:
            await message.answer("Ismni to‘g‘ri kiriting.")
            return

        users[user_id]["name"] = text
        users[user_id]["step"] = "phone"
        await message.answer("Raqamingiz:")
        return

    # 2️⃣ TELEFON
    if step == "phone":
        if not text.isdigit() or len(text) < 7:
            await message.answer("Telefon noto‘g‘ri. Masalan: 901234567")
            return

        users[user_id]["phone"] = text
        users[user_id]["step"] = "product"

        await message.answer(
            "Menyu: qaysi mahsulotimizga buyurtma bermoqchisiz?",
            reply_markup=product_menu()
        )
        return

    # 3️⃣ MAHSULOT
    if step == "product":
        if text not in PRODUCTS:
            await message.answer("Menyudan tanlang.")
            return

        users[user_id]["product"] = text
        users[user_id]["step"] = "quantity"
        await message.answer("Nechta?")
        return

    # 4️⃣ SONI
    if step == "quantity":
        if not text.isdigit():
            await message.answer("Faqat son kiriting.")
            return

        quantity = int(text)
        price = PRODUCTS[users[user_id]["product"]]
        total = quantity * price

        users[user_id]["quantity"] = quantity
        users[user_id]["total"] = total
        users[user_id]["step"] = "address"

        await message.answer(
            f"Hisob narxi: <b>{total:,} so‘m</b>\n\nManzil:"
        )
        return

    # 5️⃣ MANZIL
    if step == "address":
        if len(text) < 3:
            await message.answer("Manzilni to‘liq kiriting.")
            return

        order_id = f"AKO-{order_counter:04d}"
        order_counter += 1

        users[user_id]["address"] = text
        users[user_id]["id"] = order_id
        users[user_id]["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")

        data = users[user_id]
        save_to_excel(data)

        # Group button
        inline = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="✅ Qabul qilindi",
                    callback_data=f"done_{order_id}"
                )]
            ]
        )

        order_text = f"""
🆕 <b>YANGI BUYURTMA</b>

🆔 ID: {data['id']}
👤 {data['name']}
📞 {data['phone']}
🛒 {data['product']}
📦 {data['quantity']} dona
💰 {data['total']:,} so‘m
📍 {data['address']}
🕒 {data['date']}
"""

        await bot.send_message(GROUP_ID, order_text, reply_markup=inline)

        pay_btn = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="💳 Click / Payme orqali to‘lash",
                    url=PAYMENT_LINK
                )]
            ]
        )

        users[user_id]["step"] = "product"

        await message.answer(
            "Buyurtmangiz qabul qilindi ✅\n"
            "Operatorlarimiz tez orada siz bilan bog'lanishadi.",
            reply_markup=pay_btn
        )
        return


@dp.callback_query(lambda c: c.data.startswith("done_"))
async def done_order(callback: types.CallbackQuery):
    await callback.message.edit_text(
        callback.message.text + "\n\n✅ QABUL QILINDI"
    )
    await callback.answer("Belgilandi")


# ------------------ RUN ------------------

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
