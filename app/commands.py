import uuid
import discord
from app.storage import rooms, save_rooms, get_room_message
from app.embed import create_lobby_embed
from app.views import LobbyView
from app.timeutils import parse_time_input


def register_commands(bot):
    # create-room
    @bot.tree.command(name="create-room", description="Tạo phòng custom LMHT")
    @discord.app_commands.describe(name="Tên phòng (tối đa 20 ký tự)")
    async def create_room(interaction: discord.Interaction, name: str):

        room_id = str(uuid.uuid4())
        room_name = name.strip()[:20]

        rooms[room_id] = {
            "channel": interaction.channel_id,
            "room_name": room_name,
            "match_time": None,
            "match_timestamp": None,
            "reminded": {30: False, 15: False, 10: False, 5: False, 1: False, 0: False},
            "teamA": {r: None for r in rooms.get("__roles__", [])},
            "teamB": {r: None for r in rooms.get("__roles__", [])},
            "message_id": None,
        }

        # fallback: if roles not available, build simple structure
        if not rooms[room_id]["teamA"]:
            rooms[room_id]["teamA"] = {"Top": None, "Jungle": None, "Mid": None, "ADC": None, "Support": None}
            rooms[room_id]["teamB"] = {"Top": None, "Jungle": None, "Mid": None, "ADC": None, "Support": None}

        embed = create_lobby_embed(rooms[room_id])
        msg = None
        try:
            await interaction.response.defer()
            msg = await interaction.followup.send(embed=embed, view=LobbyView(room_id))
        except Exception:
            try:
                await interaction.response.send_message(embed=embed, view=LobbyView(room_id))
                try:
                    msg = await interaction.original_response()
                except Exception:
                    msg = None
            except Exception:
                ch = bot.get_channel(interaction.channel_id)
                if ch:
                    try:
                        msg = await ch.send(embed=embed, view=LobbyView(room_id))
                    except Exception:
                        msg = None

        if msg:
            rooms[room_id]["message_id"] = msg.id

        save_rooms()

    # set-time command
    @bot.tree.command(name="set-time", description="Đặt giờ custom")
    @discord.app_commands.describe(time="VD: 21:30, 8pm, mai 20:00")
    async def set_time(interaction: discord.Interaction, time: str):

        user = interaction.user.id
        user_rooms = []

        for rid, r in rooms.items():
            if user in r["teamA"].values() or user in r["teamB"].values():
                user_rooms.append(rid)

        if not user_rooms:
            return await interaction.response.send_message("❌ Bạn chưa ở phòng nào!", ephemeral=True)

        if len(user_rooms) == 1:
            dt = parse_time_input(time)
            if not dt:
                return await interaction.response.send_message("❌ Giờ không hợp lệ!", ephemeral=True)

            room = rooms[user_rooms[0]]
            room["match_time"] = dt.strftime("%H:%M")
            room["match_timestamp"] = int(dt.timestamp())
            room["reminded"] = {30: False, 15: False, 10: False, 5: False, 1: False, 0: False}

            msg = await get_room_message(room)
            if msg:
                try:
                    await msg.edit(embed=create_lobby_embed(room))
                except Exception:
                    pass

            save_rooms()

            try:
                return await interaction.response.send_message(
                    f"⏰ Đã đặt giờ cho **{room['room_name']}**",
                    ephemeral=True
                )
            except Exception:
                try:
                    await interaction.followup.send(f"⏰ Đã đặt giờ cho **{room['room_name']}**")
                    return
                except Exception:
                    ch = bot.get_channel(interaction.channel_id)
                    if ch:
                        await ch.send(f"⏰ Đã đặt giờ cho **{room['room_name']}**")
                    return

        view = RoomSelectView(user_rooms, time)
        try:
            await interaction.response.send_message(
                "Bạn đang ở nhiều phòng, hãy chọn phòng:",
                view=view,
                ephemeral=True
            )
        except Exception:
            try:
                await interaction.followup.send("Bạn đang ở nhiều phòng, hãy chọn phòng:")
            except Exception:
                ch = bot.get_channel(interaction.channel_id)
                if ch:
                    await ch.send("Bạn đang ở nhiều phòng, hãy chọn phòng:")


# helper select classes for set-time
class RoomSelect(discord.ui.Select):
    def __init__(self, room_ids, time_text):
        opts = []
        for rid in room_ids:
            opts.append(discord.SelectOption(
                label=rooms[rid]["room_name"], value=rid
            ))
        super().__init__(placeholder="Chọn phòng", options=opts)
        self.time_text = time_text

    async def callback(self, interaction):
        dt = parse_time_input(self.time_text)
        if not dt:
            return await interaction.response.send_message("❌ Giờ không hợp lệ!", ephemeral=True)

        rid = self.values[0]
        room = rooms[rid]

        room["match_time"] = dt.strftime("%H:%M")
        room["match_timestamp"] = int(dt.timestamp())
        room["reminded"] = {30: False, 15: False, 10: False, 5: False, 1: False, 0: False}

        msg = await get_room_message(room)
        if msg:
            await msg.edit(embed=create_lobby_embed(room))

        save_rooms()

        await interaction.response.send_message(
            f"⏰ Đã đặt giờ cho **{room['room_name']}**",
            ephemeral=True
        )


class RoomSelectView(discord.ui.View):
    def __init__(self, room_ids, time_text):
        super().__init__(timeout=30)
        self.add_item(RoomSelect(room_ids, time_text))
