import json
import os

ROOMS_FILE = "rooms.json"

ROLES = {
    "Top": "🛡️ Top",
    "Jungle": "🗡️ Rừng",
    "Mid": "🔮 Mid",
    "ADC": "🎯 Xạ thủ",
    "Support": "💖 Hỗ trợ"
}

rooms = {}
BOT = None
locks = {}


def get_room_lock(room_id):
    import asyncio
    if room_id not in locks:
        locks[room_id] = asyncio.Lock()
    return locks[room_id]


def save_rooms():
    data = {}
    for rid, r in rooms.items():
        data[rid] = {
            "channel": r["channel"],
            "room_name": r["room_name"],
            "match_time": r["match_time"],
            "match_timestamp": r["match_timestamp"],
            "reminded": r["reminded"],
            "teamA": r["teamA"],
            "teamB": r["teamB"],
            "message_id": r.get("message_id"),
        }
    with open(ROOMS_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, indent=4)


def load_rooms():
    global rooms
    if not os.path.exists(ROOMS_FILE):
        rooms = {}
        return
    try:
        with open(ROOMS_FILE, "r", encoding="utf8") as f:
            rooms = json.load(f)
    except Exception:
        rooms = {}


async def get_room_message(room):
    if BOT is None:
        return None
    channel = BOT.get_channel(room["channel"]) if room.get("channel") else None
    if not channel:
        return None
    msg_id = room.get("message_id")
    if not msg_id:
        return None
    try:
        return await channel.fetch_message(msg_id)
    except Exception:
        return None
