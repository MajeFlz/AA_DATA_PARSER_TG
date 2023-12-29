from setting_bot import dp
import openChats
import closedChats

# РОУТЫ!!!
@dp.message_handler(regexp='Спарсить данные из открытого канала')    
async def process_parser_open_parser(message):
    await openChats.parsing_open_channel(message)

@dp.message_handler(regexp='Спарсить данные из закрытого канала')
async def process_parser_open_channel(message):
    await closedChats.parser_closed_channel(message)

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)