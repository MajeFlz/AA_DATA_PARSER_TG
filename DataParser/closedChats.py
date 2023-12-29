from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher import FSMContext
from telethon import TelegramClient
from aiogram import types
from setting_bot import dp, Registration
import registration_tg_api
import os
import function_for_chat
import analys

async def parser_closed_channel(message):
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    btn1 = types.KeyboardButton('Меню')
    markup.add(btn1)
    user_id = message.from_user.id
    session_file_path = f"{user_id}.session"
    if os.path.exists(session_file_path):
        await function_for_chat.get_user_dialogs(user_id, '1', '1', '4.16.30-vxCUSTOM', message)
    else:
        await Registration.awaiting_phone.set()
        await message.reply("Ваш аккаунт не обнаружен, требуется авторизация.\nВведите ваш номер телефона в формате +79089001234")

# Проверка на сессию и РОУТ НА РЕГИСТРАЦИЮ
@dp.message_handler(Regexp(r'^\+\d{11}$'), state=Registration.awaiting_phone)
async def start_registration(message: types.Message, state: FSMContext):
    await registration_tg_api.get_user_phone(message, state)

async def parser_closed(input_peer, message, keywords):
    if input_peer is None:
        print("Ошибка: input_peer равен None.")
        return
    user_id = message.from_user.id
    async with TelegramClient(f"{user_id}.session", '1', '1', system_version='4.16.30-vxCUSTOM') as client:
        try:
            messages = await client.get_messages(input_peer, limit=1000)
        except Exception as e:
            print(f"Ошибка при получении сообщений: {e}")
            return
        # Создаем временный файл
        directory_path = f"users/{user_id}/"
        os.makedirs(directory_path, exist_ok=True)
        file_path = f"{directory_path}/{input_peer}_messages.txt"
        with open(file_path, "w", encoding="utf-8") as file:
            for msg in messages:
                # Проверяем на пустое сообщение и записываем текст сообщения в файл
                if msg.text is not None:
                    file.write(msg.text + "\n---MESSAGE_SEPARATOR---\n") 
        result =await analys.analyse_interests(file_path, keywords)
       
        for item in result[:10]:
                await message.answer(item)
        os.remove(file_path)# удаляем             
       
