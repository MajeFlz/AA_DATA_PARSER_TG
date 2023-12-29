from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
import config

# Создаем бота и диспетчер
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# стейты на ожидание ввода данных(номер, код)
class Registration(StatesGroup):
    awaiting_phone = State()
    awaiting_code = State()
    awaiting_link = State()
    awaiting_keywords_open = State()
    awaiting_keywords_closed = State()
    awaiting_chat_choice = State()
    awaiting_phone_for_code = State()
    awaiting_code_for_closed = State()
    feature_autorization = State()

class Parser():
    status = True
    user_id = None

@dp.message_handler(Command("start"), state="*") # Начало
async def start_message(message):
    text = (f'Привет {message.from_user.first_name}, я бот парсер информации.'
            'Выберите, что вы хотите из кнопок ниже:')
    user_id = message.from_user.id
    print(user_id)
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

@dp.message_handler(Command("stop"), state="*")
async def stop(message: types.Message, state: FSMContext):
    await state.finish()
    markup = await main_menu()
    await message.reply("Операция закончена.", reply_markup=markup)

@dp.message_handler(Command("menu"), state="*")
async def menu(message: types.Message):
    text = (f'Вы в главном меню. Просто выберите что делать дальше:')
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

@dp.message_handler(Command("autorization"), state="feature_autorization")
async def autorization(message: types.Message):
    text = (f'Если вы хотите авторизироваться для парсинга закрытых чатов\nвведите ваш телефон:')
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)
    await Registration.awaiting_phone_for_code.set()

@dp.message_handler(state=Registration.awaiting_phone_for_code)
async def process_autorization(message, state: FSMContext):
    phone_number = message.text
    print(phone_number)
    text = (f'Сейчас вам придет код Telegram, введите его, чтобы закончить авторизацию')
    await Registration.awaiting_code_for_closed.set()
    await state.finish()
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

@dp.message_handler(state=Registration.awaiting_code_for_closed)
async def autorization_complete(message, state: FSMContext):
    code = message.text
    print(code)
    await state.finish()

@dp.message_handler(Command("code"), state="*")
async def menu(message: types.Message):
    text = (f'Вы в главном меню. Просто выберите что делать дальше:')
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)  

@dp.message_handler(Command("help"), state="*")
async def commands(message: types.Message):
    text = (f"Список доступных команд:\n"
            f"/start - Начать взаимодействие с ботом\n"
            f"/stop - Закончить операцию\n"
            f"/menu - Вернуться в главное меню\n"
            f"/parser_on/off - Включить/Выключить парсер в текущем времени")
    
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

@dp.message_handler(Command("parser_on"), state="*")
async def parser_on(message: types.Message):
    Parser.status = True
    user_id = message.from_user.id
    Parser.user_id = user_id
    text = ("Теперь вы можете включить парсер. Напишите, включить парсер")

    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

@dp.message_handler(Command("parser_off"), state="*")
async def cparser_off(message: types.Message):
    Parser.status = False
    text = ("Парсер в текущем времени успешно отключен")
    markup = await main_menu()
    await message.answer(text, reply_markup=markup)

# Кнопочки
async def main_menu():
    markup = types.reply_keyboard.ReplyKeyboardMarkup(row_width=2,resize_keyboard=True)
    btn1 = types.KeyboardButton('Спарсить данные из открытого канала')
    btn2 = types.KeyboardButton('Спарсить данные из закрытого канала')
    btn3 = types.KeyboardButton('Фото котиков')
    markup.add(btn1, btn2, btn3)
    return markup        