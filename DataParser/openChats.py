from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Regexp
from aiogram.types import ReplyKeyboardRemove
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from setting_bot import dp, Registration
import config
import os
import csv
from telethon.tl.types import PeerChannel
import analys

# вступление в группу
async def join_channel(client, channel_link):
    try:
        entity = await client.get_entity(channel_link)
        chat_id = entity.id
        if chat_id:
            await client(JoinChannelRequest(entity))
            print('успешно вступил')
        return chat_id
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# собирание сообщений
async def get_chat_messages(client, chat_id, limit=1000):
    try:
        messages = await client.get_messages(PeerChannel(chat_id), limit=limit)

        return messages
    except Exception as e:
        print(f"Ошибка при получении сообщений из чата: {e}")
        return []

# просим ссылку        
async def parsing_open_channel(message):
    text = 'Укажите ссылку на канал в формате: https://t.me/alishev_g'
    await Registration.awaiting_link.set() # устанавливаем стейт 
    await message.answer(text, reply_markup=ReplyKeyboardRemove()) 

# если есть стейт и ссылка валидна
@dp.message_handler(Regexp(r'https?://(?:web\.telegram\.org/a/#-1001475558991|t\.me/(\w+)|t\.me/(\w+))'), state=Registration.awaiting_link)
async def process_channel_link(message: types.Message, state: FSMContext):
    channel_link = message.text  # берем ссылку
    async with TelegramClient(config.PHONE + '.session', config.API_ID, config.API_HASH,
                              system_version='4.16.30-vxCUSTOM') as client:
        # Пытаемся вступить в группу по ссылке
        chat_id = await join_channel(client, channel_link)
        if chat_id:
            await state.update_data(chat_id=chat_id)
            await Registration.awaiting_keywords_open.set()
            text = "Введите ключевые слова для фильтрации (разделите пробелом):"
            await message.answer(text, reply_markup=ReplyKeyboardRemove())
        else:
            # Если не удалось вступить в группу, можно предпринять соответствующие действия
            await message.answer("Не удалось вступить в группу. Пожалуйста, убедитесь в правильности ссылки.")

# берем чаты
@dp.message_handler(state=Registration.awaiting_keywords_open)
async def process_parser_on_keywords_open(message: types.Message, state: FSMContext):
    data = await state.get_data()
    keywords = message.text.split()
    chat_id = data.get('chat_id')
    await state.finish()
    async with TelegramClient(config.PHONE+'.session', config.API_ID, config.API_HASH, system_version='4.16.30-vxCUSTOM') as client:
        user_id = message.from_user.id
        messages = await get_chat_messages(client, chat_id) # получаем сообщения
        # Создаем временный файл
        if messages is not None:
            directory_path = f"users/{user_id}/" 
            os.makedirs(directory_path, exist_ok=True) # создаем директорию, если её нет
            file_path = f"users/{user_id}/open_messages.txt"
            with open(file_path, "w", encoding="utf-8") as file:
                for msg in messages:
                # Проверяем, что текст сообщения не является None
                    if msg.text is not None:
                        file.write(msg.text + "\n---MESSAGE_SEPARATOR---\n")
            result =await analys.analyse_interests(file_path, keywords)
            for item in result[:10]:
                await message.answer(item)
            os.remove(file_path)# удаляем
            #await analys.send_messages_to_chat(bot, message.chat.id, messages, keywords)    

