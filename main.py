from telethon import TelegramClient, events
from aiogram import Bot, Dispatcher, types, executor
import asyncio
import re

api_id = 11066459  # Получить https://my.telegram.org/auth
api_hash = '03a2863d458f425995b86fcbd9f910a1'
source_channels = [-1234567890, -1234567890]  # откуда берём посты
destination_channels = {
    -1234567890: "<b><a href='https://t.me/'></a></b>",
    -1234567890: "<b><a href='https://t.me/'></a></b>"
}  # ID основного канала: Описание(можно использовать несколько каналов)

bot_token = '7025449311:AAFd6ccTTS8xqz4KtlwuCTnbfkHXKU8vkT4'  # Токен бота для логов
log_chat_id = -1234567890  # ID чата, куда будут отправляться логи
stop_words = ['https', 'казино', 'ставки', 'пока не удалили', 'игра', 'крипта', '@', '.', 'послед', '-']  # Заменить на другие исключения

client = TelegramClient('vor_postov', api_id, api_hash)
bot = Bot(token=bot_token, parse_mode='HTML')
dp = Dispatcher(bot)

async def start_telegram_client():
    await client.start()
    try:
        for channel in source_channels:
            access = await client.get_entity(channel)
            name_channel = access.title
            await bot.send_message(log_chat_id, f'<b>Канал донор</b> <code>{name_channel}</code>:<code>{channel}</code> <b>доступен!</b>')
        for channel_id, description in destination_channels.items():
            access = await client.get_entity(channel_id)
            name_channel = access.title
            await bot.send_message(log_chat_id, f'<b>Ваш канал</b> <code>{name_channel}</code>:<code>{channel_id}</code> <b>доступен!</b>')
    except Exception as e:
        await bot.send_message(log_chat_id, f'Ошибка: {e}')
        return

def remove_links(text):
    return re.sub(r'http\S+|www\S+|@\S+', '', text)

@client.on(events.Album(chats=source_channels))
async def new_album(event):
    original_message = event.original_update.message.message
    clean_message = remove_links(original_message)

    # Проверяем наличие запрещенных слов в сообщении
    if any(stop_word in clean_message for stop_word in stop_words):
        log_message = f"<i><b>Сообщение содержит запрещённые слова.\n\n</b></i><code>{clean_message}</code>"
        await bot.send_message(log_chat_id, log_message)
        return

    for channel_id, description in destination_channels.items():
        await client.send_message(
            entity=channel_id,
            file=event.messages,
            message=description,
            parse_mode='html'
        )
    await bot.send_message(log_chat_id, f"<b>Сообщение успешно отправлено!</b>")

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    original_message = event.message.message
    clean_message = remove_links(original_message)

    # Проверяем наличие запрещенных слов в сообщении
    if any(stop_word in clean_message for stop_word in stop_words):
        log_message = f"<i><b>Сообщение содержит запреты.\n\n</b></i><code>{clean_message}</code>"
        await bot.send_message(log_chat_id, log_message)
        return

    if event.message.grouped_id:
        pass
    else:
        if event.message.media:
            for channel_id, description in destination_channels.items():
                await client.send_file(
                    channel_id,
                    event.message.media,
                    caption=description,
                    parse_mode='html'
                )
            await bot.send_message(log_chat_id, f"<b>Сообщение успешно отправлено!</b>")
        else:
            for channel_id, description in destination_channels.items():
                await client.send_message(channel_id, description, parse_mode='html')
            await bot.send_message(log_chat_id, f"<b>Сообщение успешно отправлено!</b>")

async def main():
    await start_telegram_client()
    await dp.start_polling()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
