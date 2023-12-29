from telethon import TelegramClient
from setting_bot import dp, Registration
from aiogram.dispatcher import FSMContext
from aiogram import types
import closedChats 

async def get_user_dialogs(user_id, api_id, api_hash, version, message):        
    async with TelegramClient(f"{user_id}.session", api_id, api_hash, system_version=version) as client:
        await message.answer('Сессия создана!\nВы всегда можете закрыть сессию командой /session_off\nПосле закрытия сессии придется авторизироваться внова')
        dialogs = await client.get_dialogs()
        chats_dict = {}
        for i, dialog in enumerate(dialogs, 1):
            chats_dict[i] = {'title': dialog.title, 'id': dialog.id}
        
        state = dp.current_state(user=message.from_user.id, chat=message.chat.id)
        await Registration.awaiting_chat_choice.set()
        await state.update_data(chats=chats_dict)
        
        formatted_chats = "\n".join([f"{num}. {chat['title']}" for num, chat in chats_dict.items()])
        await message.answer("Ваши чаты:\n" + formatted_chats)
        await message.answer('Выберите чат для парсинга')

# Обработчик ввода номера чата
@dp.message_handler(state=Registration.awaiting_chat_choice)
async def process_chat_choice(message: types.Message, state: FSMContext):
    try:
        chat_choice = int(message.text)
        data = await state.get_data()
        chats_dict = data.get('chats', {})
        await state.finish()
        if 1 <= chat_choice <= len(chats_dict):
            chosen_chat_info = chats_dict[chat_choice]
            peer_id = chosen_chat_info['id']
            await state.update_data(peer_id=peer_id)
            await message.answer("Введите ключевые слова для фильтрации (разделите пробелом):")
            await Registration.awaiting_keywords_closed.set()
        else:
            await message.answer("Такого номера чата нет")
    except ValueError:
        await message.answer("Введите число")

@dp.message_handler(state=Registration.awaiting_keywords_closed)
async def process_keywords_input(message: types.Message, state: FSMContext):
    keywords = message.text.split()
    data = await state.get_data()
    input_peer = data.get('peer_id')
    await state.finish()
    if input_peer:
        await closedChats.parser_closed(input_peer, message, keywords)
        await state.finish()
    else:
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")        
