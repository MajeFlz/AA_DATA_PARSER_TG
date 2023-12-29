from telethon import TelegramClient, events
from setting_bot import Parser

if Parser.user_id is not None:
    user_id = Parser.user_id
    client = TelegramClient(f"{user_id}.session", '1', '1')
    @client.on(events.NewMessage)
    async def on_new_message(event):
        await handle_messages(event)

    async def handle_messages(event):
        if Parser.status:
            message = event.message
            if message == "перец":
                print('1')
            input_peer = message.to_id.channel_id if message.is_channel else message.to_id.chat_id
else:
    print("user_id не установлен.")


