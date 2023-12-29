from telethon.client.auth import AuthMethods
from aiogram import types
from aiogram.dispatcher import FSMContext

class CustomAuthMethods(AuthMethods):

    def __init__(self, custom_phone, custom_password, *args, **kwargs):
        self.custom_phone = custom_phone
        self.custom_password = custom_password

    async def handle_user_input(self, message: types.Message, state: FSMContext, **kwargs) -> None:
        data = await state.get_data()
        phase = data.get('phase')

        if phase == 'phone':
            phone = message.text
            await message.answer(f'Thank you! Your phone: {phone}')
        elif phase == 'password':
            password = message.text
            await message.answer(f'Thank you! Your password: {password}')

    async def start(
            self,
            phone=None,
            password=None,
            bot_token=None,
            force_sms=False,
            code_callback=None,
            first_name='New User',
            last_name='',
            max_attempts=3):

        # Ваш код start, который вы хотите выполнить

        # Предположим, что у вас есть объект state, который передается в метод
        state = FSMContext()  # Замените на фактическую инициализацию state

        await self.handle_user_input(message=types.Message, state=state)
