import telebot

TOKEN = "8427218470:AAFNC81mmMl8d0op2xJzS7I8Vg5vOC8vPbo"
ADMIN_ID = 1028958055

bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Assalomu alaykum! 😊\n\nIsm va familiyangizni birga yozing (masalan: Ali Valiyev)")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id] = {}
    user_data[message.chat.id]['name'] = message.text

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton("📞 Raqam yuborish", request_contact=True)
    markup.add(button)

    bot.send_message(message.chat.id, "Telefon raqamingizni yuboring:", reply_markup=markup)
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    user_data[message.chat.id]['phone'] = phone

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("6L - 6 ming", "8L - 8 ming")
    markup.add("15L - 15 ming")

    bot.send_message(message.chat.id, "Mahsulotni tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def get_product(message):
    if message.chat.id in user_data:
        name = user_data[message.chat.id]['name']
        phone = user_data[message.chat.id]['phone']
        product = message.text

        text = f"🛒 Yangi zakaz!\n\n👤 {name}\n📞 {phone}\n💧 {product}"

        bot.send_message(ADMIN_ID, text)
        bot.send_message(message.chat.id, "✅ Zakazingiz qabul qilindi!")

        del user_data[message.chat.id]

bot.polling()
