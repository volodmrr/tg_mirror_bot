from telethon import TelegramClient, events
import asyncio
from .logger import logger
from .config import API_ID, API_HASH, SOURCE_CHANNELS, TARGET_CHANNEL
from album_utils import flush_album, album_buffer


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
        msg = event.message
        chat_id = event.chat_id

        source = next((s for s in sources if s["chat_id"] == chat_id), None)
        if source and source["thread_id"] is not None:
            if msg.reply_to and msg.reply_to.reply_to_top_id != source["thread_id"]:
                return

        try:
            if msg.grouped_id:
                gid = (msg.grouped_id, chat_id)
                if gid not in album_buffer:
                    album_buffer[gid] = []
                    asyncio.get_event_loop().call_later(10, asyncio.create_task, flush_album(gid, target))
                album_buffer[gid].append(msg)

            elif msg.media:
                await client.send_file(target, msg.media, caption=msg.message or "")
                logger.info(f"Mirrored media from {chat_id}: {msg.id}")

            elif msg.message:
                await client.send_message(target, msg.message)
                logger.info(f"Mirrored text from {chat_id}: {msg.message}")

            else:
                warn_text = f"⚠️ Warning: unsupported message type (id {msg.id})"
                await client.send_message(target, warn_text)
                logger.warning(warn_text)

        except Exception as e:
            error_text = f"❌ Error mirroring message {msg.id} from {chat_id}: {e}"
            try:
                await client.send_message(target, error_text)
            except Exception as inner_e:
                logger.error(f"Failed to send error to target: {inner_e}")
            logger.exception(error_text)

    await client.run_until_disconnected()
