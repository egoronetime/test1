import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Для установки московского часового пояса

# Данные для Telethon
api_id = 17131727
api_hash = '26d3f347b2c528f06f7ae1f10bbdb6f9'
channel_id = -1001993441703  # Основной канал ID
chat_id = -1002490325762  # ID группы для логов
topic_id = 595  # ID топика для логов

# Создаем новую сессию с уникальным именем
client = TelegramClient('new_session_name', api_id, api_hash)

# Функция для отправки лога в указанный топик Telegram
async def send_log_to_telegram(message):
    try:
        await client.send_message(chat_id, message, reply_to=topic_id, parse_mode='html')
    except Exception as e:
        print(f"Ошибка при отправке лога в Telegram: {e}")

# Функция для проверки поста, опубликованного примерно 24 часа назад
async def check_views():
    now = datetime.now(ZoneInfo("Europe/Moscow"))
    target_time = now - timedelta(hours=24)
    time_window_start = target_time - timedelta(hours=2)  # 22 часа назад
    time_window_end = target_time + timedelta(hours=2)    # 26 часов назад

    closest_message = None
    closest_time_difference = timedelta.max

    # Поиск сообщения, опубликованного примерно 24 часа назад, без ограничения по offset_date
    async for message in client.iter_messages(channel_id, limit=100):  # Установлен лимит в 100 сообщений
        # Проверка, что сообщение находится в пределах временного окна
        if time_window_start <= message.date <= time_window_end:
            # Сравниваем разницу во времени, чтобы найти максимально близкое сообщение
            time_difference = abs(message.date - target_time)
            if time_difference < closest_time_difference:
                closest_time_difference = time_difference
                closest_message = message

        # Прерываем цикл, если дата сообщения выходит за нижний предел временного окна
        if message.date < time_window_start:
            break

    # Если найдено подходящее сообщение, отправляем его количество просмотров
    if closest_message:
        views = closest_message.views
        cpm_base = views / 1000  # Количество тысяч просмотров

        # Расчеты для различных ставок
        cpm_250 = cpm_base * 250
        cpm_300 = cpm_base * 300
        cpm_350 = cpm_base * 350

        # Получаем текущую дату и время в московском времени
        current_date_msk = datetime.now(ZoneInfo("Europe/Moscow"))
        formatted_current_date = current_date_msk.strftime("%Y-%m-%d %H:%M:%S")

        message_link = f"https://t.me/c/{str(channel_id)[4:]}/{closest_message.id}"
        log_message = (
            f"📊 Количество просмотров поста за 24 часа:\n\n"
            f"🔗 <a href=\"{message_link}\">Ссылка на пост</a>\n"
            f"👁 {views} просмотров\n\n"
            f"💵 <b>Расчет по CPM</b>\n\n"
            f"• 250 — <code>{cpm_250:.2f}</code>\n"
            f"• 300 — <code>{cpm_300:.2f}</code>\n"
            f"• 350 — <code>{cpm_350:.2f}</code>\n\n"
            f"📅 Текущая дата и время (МСК): <code>{formatted_current_date}</code>"
        )
        await send_log_to_telegram(log_message)
    else:
        # Если постов в заданном окне нет, уведомляем об этом
        await send_log_to_telegram("⚠️ Нет сообщений, опубликованных примерно 24 часа назад.")

# Обработчик для команды "просмотры"
@client.on(events.NewMessage(pattern=r'^просмотры$', chats=chat_id))
async def handle_views_command(event):
    await check_views()

# Запускаем функцию каждую часовую отметку
async def schedule_hourly_task():
    while True:
        await check_views()
        await asyncio.sleep(3600)  # Задержка 1 час

# Асинхронная функция для запуска клиента и задач
async def main():
    await client.start()
    # Запускаем фоновую задачу
    client.loop.create_task(schedule_hourly_task())
    await client.run_until_disconnected()

# Запуск клиента
if __name__ == '__main__':
    asyncio.run(main())