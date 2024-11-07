import telebot

# Задаем токен бота
TOKEN = '7613556482:AAEsTZzPg7NBuFm75kKVwNGeD9_6mTS7_0I'
bot = telebot.TeleBot(TOKEN)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Добро пожаловать!")

# Запуск бота
bot.polling()