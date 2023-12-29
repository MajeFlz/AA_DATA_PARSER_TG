from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = '6753175489:AAHqS_jOc7ldQX0I1mFez-OiKv2zVnj0kyo'

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Registration(StatesGroup):
    awaiting_phone = State()
    awaiting_code = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Добро пожаловать! Для продолжения регистрации введите ваш номер телефона.")
    await Registration.awaiting_phone.set()


@dp.message_handler(state=Registration.awaiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    # Обработка номера телефона (валидация, сохранение и т.д.)
    phone_number = message.text

    # Предположим, что номер телефона валиден
    await state.update_data(phone=phone_number)

    # Запросить ввод кода
    await message.reply("Отлично! Теперь введите код подтверждения.")
    await Registration.awaiting_code.set()


@dp.message_handler(state=Registration.awaiting_code)
async def process_code(message: types.Message, state: FSMContext):
    # Обработка кода (валидация, сохранение и т.д.)
    code = message.text

    # Получить номер телефона из сохраненных данных
    data = await state.get_data()
    phone_number = data.get('phone')

    # Предположим, что код подтверждения валиден
    await message.reply(f"Регистрация завершена! Номер телефона: {phone_number}, Код подтверждения: {code}")

    # Завершить процесс регистрации
    await state.finish()


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)