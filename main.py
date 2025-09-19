from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNELS = [s.strip() for s in os.getenv("SOURCE_CHANNELS", "").split(",") if s.strip()]
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))

client = TelegramClient("mirror_session", API_ID, API_HASH)
album_buffer = {}


def parse_source(raw: str):
    """
    Parse a source string.
    - "-1001234567890" (chat only)
    - "-1001234567890_98765" (chat + thread)
    Returns dict {chat_id, thread_id}
    """
    if "_" in raw:
        chat_id_str, thread_id_str = raw.split("_", 1)
        return {"chat_id": int(chat_id_str), "thread_id": int(thread_id_str)}
    return {"chat_id": int(raw), "thread_id": None}


async def main():
    print("Connecting...")
    await client.start(
        code_callback=lambda: input("Enter the login code you received: "),
    )
    print("Connected!")

    sources = [parse_source(s) for s in SOURCE_CHANNELS]
    target = await client.get_entity(TARGET_CHANNEL)

    print("Listening for new messages in sources:", sources)

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
                    asyncio.get_event_loop().call_later(
                        10, asyncio.create_task, flush_album(gid, target)
                    )
                album_buffer[gid].append(msg)

            elif msg.media:
                await client.send_file(
                    target,
                    msg.media,
                    caption=msg.message or ""
                )
                print(f"Mirrored media from {chat_id}: {msg.id}")

            elif msg.message:
                await client.send_message(target, msg.message)
                print(f"Mirrored text from {chat_id}: {msg.message}")

            else:
                warn_text = f"⚠️ Warning: unsupported message type (id {msg.id})"
                await client.send_message(target, warn_text)
                print(warn_text)

        except Exception as e:
            error_text = f"❌ Error mirroring message {msg.id} from {chat_id}: {e}"
            try:
                await client.send_message(target, error_text)
            except Exception as inner_e:
                print("Failed to send error to target:", inner_e)
            print(error_text)

    await client.run_until_disconnected()


async def flush_album(gid, target):
    try:
        if gid not in album_buffer:
            return
        msgs = album_buffer.pop(gid, [])
        files = [m.media for m in msgs if m.media]
        caption = next((m.message for m in msgs if m.message), "")
        if files:
            await client.send_file(target, files, caption=caption)
            print(f"Mirrored album ({len(files)} media) from {gid[1]}")
        else:
            warn_text = f"⚠️ Warning: empty/unsupported album (group {gid})"
            await client.send_message(target, warn_text)
            print(warn_text)
    except Exception as e:
        album_buffer.pop(gid, None)
        error_text = f"❌ Error sending album {gid}: {e}"
        try:
            await client.send_message(target, error_text)
        except Exception as inner_e:
            print("Failed to send album error to target:", inner_e)
        print(error_text)


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
