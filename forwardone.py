from telethon import TelegramClient, events

# Параметры для подключения
api_id = 20205260
api_hash = '21d8757582cc79d1d7911606d53b55be'

# Параметры каналов и логирования
channels = [
    {"source": -1002008068553, "target": -1002266491534, "source_name": "За 5 секунд до", "target_name": "R(s)"},  # Основные каналы
    {"source": -1001993441703, "target": -1002420062159, "source_name": "DEATH", "target_name": "R(d)"},          # Основные каналы
    {"source": -1002472771049, "target": -1002251094320, "source_name": "Тестовый канал 1", "target_name": "Тестовый канал 2"}  # Тестовые каналы
]

# Параметры для логирования
log_chat_id = -1002490325762  # Новый ID группы для логов
log_topic_id = 543  # Обновленный ID топика для логов (если необходимо)

# Создаем клиент
client = TelegramClient('forward_bot', api_id, api_hash)

# Функция для отправки лога в указанный топик Telegram
async def send_log_to_telegram(message):
    try:
        await client.send_message(log_chat_id, message, reply_to=log_topic_id, parse_mode='html')
    except Exception as e:
        print(f"Ошибка при отправке лога в Telegram: {e}")

# Функция для обработки новых сообщений из определенного канала
def set_channel_listener(channel):
    @client.on(events.NewMessage(chats=channel["source"]))
    async def forward_message(event):
        try:
            # Пытаемся переслать сообщение в целевой канал
            forwarded_message = await client.forward_messages(channel["target"], event.message)

            # Генерация ссылок на сообщения
            source_message_link = f"https://t.me/c/{str(channel['source'])[4:]}/{event.message.id}"
            target_message_link = f"https://t.me/c/{str(channel['target'])[4:]}/{forwarded_message.id}"
            timestamp = f"<code>{event.message.date.strftime('%Y-%m-%d %H:%M:%S')}</code>"

            # Формируем сообщение для лога с зашитыми ссылками и информацией о каналах
            log_message = (f"<b>Сообщение:</b>\n\n<code>{event.message.message}</code>\n\n"
                           f"↩️ C канала: '<a href=\"{source_message_link}\">{channel['source_name']}</a>'\n"
                           f"✅ На канал: '<a href=\"{target_message_link}\">{channel['target_name']}</a>'\n\n"
                           f"{timestamp}")

            # Отправляем лог в указанный топик
            await send_log_to_telegram(log_message)

        except Exception as e:
            # Логирование ошибки пересылки сообщения
            error_log = f"Ошибка при пересылке сообщения из канала '{channel['source_name']}' в канал '{channel['target_name']}': {str(e)}"
            await send_log_to_telegram(error_log)
            print(error_log)

# Создаем обработчики событий для каждого канала
for channel in channels:
    set_channel_listener(channel)

# Запуск бота
with client:
    print("Бот запущен и слушает новые сообщения...")
    client.run_until_disconnected()