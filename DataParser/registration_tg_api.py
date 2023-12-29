import requests
import re
from fake_useragent import UserAgent
from aiogram.dispatcher.filters import Regexp
from aiogram.dispatcher import FSMContext
from aiogram import types
from setting_bot import dp, Registration
import function_for_chat

async def get_user_phone(message, state):
    phone = message.text
    headers = {
        'user-agent': UserAgent().random
    }

    payload = {
        'phone': phone
    }

    response = requests.post('https://my.telegram.org/auth/send_password', headers=headers, params=payload)
    random_hash = response.json()['random_hash']
    await Registration.awaiting_code.set()
    await message.reply("Пожалуйста, введите код, полученный в Telegram.")
    await state.update_data(phone=phone, random_hash=random_hash, headers=headers)

@dp.message_handler(Regexp(r'^[A-Za-z0-9_-]{11}$'), state=Registration.awaiting_code)
async def get_user_code(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        phone = data['phone']
        random_hash = data['random_hash']
        headers = data['headers']

    password = message.text

    payload = {
        'phone': phone, 
        'random_hash': random_hash, 
        'password': password
    }

    response = requests.post('https://my.telegram.org/auth/login', headers=headers, params=payload)
    cookie = response.headers['Set-Cookie'].split(";")[0]

        # Отправляем cookies (из прошлого запроса) -> понимаем, зареган или нет
    headers2 = {
        'user-agent': UserAgent().random, 
        'Cookie': cookie
    }

    response = requests.get('https://my.telegram.org/apps', headers=headers2)
    content = str(response.content)

    #
    # Логика, если пользователь зарегистрирован
    #
    if content.find('onclick="this.select();">') != -1:
        indexStartForId = content.find('onclick="this.select();">') + 33
        indexStopForId = content.find('</span>') - 9
        id = content[indexStartForId:indexStopForId:]

        content = content[indexStopForId::]

        indexStartForHash = content.find('onclick="this.select();">') + 25
        indexStopForHash = indexStartForHash + 80
        hash = re.search(r"([a-z0-9]+)", content[indexStartForHash:indexStopForHash:]).group(1)
    #
    # Логика, если пользователь НЕ зарегистрирован
    #
    else:
        indexStart = content.find('name="hash" value="') + 19
        indexStop = indexStart + 20
        hash = re.search(r"([a-z0-9]+)", content[indexStart:indexStop:]).group(1)

        headers = {
            'user-agent': UserAgent().random,
            'Cookie': cookie
        }

        payload = {
            "hash": hash,
            "app_title": "TestSearchMessage",
            "app_shortname": "TestSearch",
            "app_url": "",
            "app_platform": "android",
            "app_desc": ""
        }

        response = requests.post('https://my.telegram.org/apps/create', headers=headers, params=payload)

        headers = {
            'user-agent': UserAgent().random, 
            'Cookie': cookie
        }

        response = requests.get('https://my.telegram.org/apps', headers=headers)
        content = str(response.content)

        indexStartForId = content.find('onclick="this.select();">') + 33
        indexStopForId = content.find('</span>') - 9
        id = content[indexStartForId:indexStopForId:]

        content = content[indexStopForId::]

        indexStartForHash = content.find('onclick="this.select();">') + 25
        indexStopForHash = indexStartForHash + 80
        hash = re.search(r"([a-z0-9]+)", content[indexStartForHash:indexStopForHash:]).group(1)

    api_id = id
    api_hash = hash
    user_id = message.from_user.id
    # Обходим авторизацию, через костыль функции, чтобы не писать дополнение метода в классе TelegramClient
    await Registration.feature_autorization.set()
    await message.answer('Для продолжения авторизации пропишите команду /autorization и следуйте инструкции')
    await function_for_chat.get_user_dialogs(user_id, f"{api_id}", f"{api_hash}", '4.16.30-vxCUSTOM', message)
