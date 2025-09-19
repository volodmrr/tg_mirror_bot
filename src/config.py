import os
from dotenv import load_dotenv

load_dotenv()


def parse_source(raw: str):
    if "_" in raw:
        chat_id_str, thread_id_str = raw.split("_", 1)
        return {"chat_id": int(chat_id_str), "thread_id": int(thread_id_str)}
    return {"chat_id": int(raw), "thread_id": None}

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNELS = [parse_source(s.strip()) for s in os.getenv("SOURCE_CHANNELS", "").split(",") if s.strip()]
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL"))
