from telethon import TelegramClient
from .logger import logger

album_buffer = {}

async def flush_album(gid, target, client: TelegramClient):
    try:
        if gid not in album_buffer:
            return
        msgs = album_buffer.pop(gid, [])
        files = [m.media for m in msgs if m.media]
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
