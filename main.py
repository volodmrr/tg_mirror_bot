from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
PASSWORD = os.getenv("PASSWORD", "")
SOURCE_CHANNEL = os.getenv("SOURCE_CHANNEL")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")


client = TelegramClient("mirror_session", API_ID, API_HASH)
album_buffer = {}

def resolve_entity(value: str | int):
    if isinstance(value, str):
        if value.lstrip("-").isdigit():
            return int(value)
        return value.strip()
    return value

async def main():
    print("Connecting...")
    await client.start(
        phone=lambda: PHONE,
        password=lambda: PASSWORD if PASSWORD else None,
        code_callback=lambda: input("Enter the login code you received: "),
    )
    print("Connected!")

    source = await client.get_entity(resolve_entity(SOURCE_CHANNEL))
    target = await client.get_entity(resolve_entity(TARGET_CHANNEL))

    print("Listening for new messages in source channel...")

    @client.on(events.NewMessage(chats=source))
    async def handler(event):
        msg = event.message
        try:
            if msg.grouped_id:
                gid = msg.grouped_id
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
                print("Mirrored media:", msg.id)

            elif msg.message:
                await client.send_message(target, msg.message)
                print("Mirrored text:", msg.message)

            else:
                warn_text = f"⚠️ Warning: unsupported message type (id {msg.id})"
                await client.send_message(target, warn_text)
                print(warn_text)

        except Exception as e:
            error_text = f"❌ Error mirroring message {msg.id}: {e}"
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
            print(f"Mirrored album with {len(files)} media")
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
