from telethon import TelegramClient
import asyncio
from .logger import logger

album_buffer = {}

async def flush_album(gid, target, client: TelegramClient):
    try:
        if gid not in album_buffer:
            return
        msgs = album_buffer.pop(gid, [])
        files = [await m.download_media(file=bytes) for m in msgs if m.media]
        caption = next((m.message for m in msgs if m.message), "")
        if files:
            await client.send_file(target, files, caption=caption)
            logger.info(f"Mirrored album ({len(files)}) from {gid[1]}")
        else:
            warn_text = f"⚠️ Warning: empty/unsupported album (group {gid})"
            await client.send_message(target, warn_text)
            logger.warning(warn_text)
    except Exception as e:
        album_buffer.pop(gid, None)
        error_text = f"❌ Error sending album {gid}: {e}"
        try:
            await client.send_message(target, error_text)
        except Exception as inner_e:
            logger.error(f"Failed to send album error to target: {inner_e}")
        logger.exception(error_text)

async def process_message(event, client, target):
    msg = event.message
    chat_id = event.chat_id

    try:
        if msg.grouped_id:
            gid = (msg.grouped_id, chat_id)
            if gid not in album_buffer:
                album_buffer[gid] = []
                asyncio.get_event_loop().call_later(
                    10, asyncio.create_task, flush_album(gid, target, client)
                )
            album_buffer[gid].append(msg)

        elif msg.media:
            file = await msg.download_media(file=bytes)
            await client.send_file(target, file, caption=msg.message or "")
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
