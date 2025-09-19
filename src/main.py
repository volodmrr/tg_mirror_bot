from telethon import TelegramClient, events
from .logger import logger
from .config import API_ID, API_HASH, SOURCE_CHANNELS, TARGET_CHANNEL
from .msg_handler import process_message

client = TelegramClient("mirror_session", API_ID, API_HASH)
    

async def main():
    logger.info("Connecting...")
    await client.start(code_callback=lambda: input("Enter the login code you received: "))
    logger.info("Connected")

    sources = SOURCE_CHANNELS
    target = await client.get_entity(TARGET_CHANNEL)

    logger.info(f"Listening for new messages in sources: {sources}")

    @client.on(events.NewMessage(chats=[s["chat_id"] for s in sources]))
    async def handler(event):
        chat_id = event.chat_id
        source = next((s for s in sources if s["chat_id"] == chat_id), None)
        if source and source["thread_id"] is not None:
            if event.message.reply_to and event.message.reply_to.reply_to_top_id != source["thread_id"]:
                return

        await process_message(event, client, target)

    await client.run_until_disconnected()
