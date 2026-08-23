import os
import re
import uuid
import random
import json
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

import app.storage as storage
from app.storage import ROLES, rooms, save_rooms, load_rooms, get_room_message
from app.embed import create_lobby_embed
from app.timeutils import parse_time_input
from app.randomize import do_random_keep, do_random_all

# wire bot into storage module so get_room_message can use it
storage.BOT = bot

# ensure rooms are loaded
load_rooms()


# ============================
# BOT READY
# ============================

@bot.event
async def on_ready():
    print(f"Đã đăng nhập dưới tên {bot.user}")
    try:
        await bot.tree.sync()
    except:
        pass
    update_countdowns.start()


import app.commands as commands_module

# register commands (create-room, set-time)
commands_module.register_commands(bot)


# ============================
# LOBBY VIEW (UI1 + Layout C + Random)
# ============================

class LobbyView(discord.ui.View):
    def __init__(self, room_id):
        super().__init__(timeout=None)
        self.room_id = room_id

    async def pick(self, interaction, team, role):
        room = rooms[self.room_id]
        user = interaction.user.id

        if room[team][role] not in (None, user):
            return await interaction.response.send_message(
                f"❌ Lane **{ROLES[role]}** đã có người!",
                ephemeral=True
            )

        for t in [room["teamA"], room["teamB"]]:
            for r in ROLES:
                if t[r] == user:
                    t[r] = None

        room[team][role] = user

        msg = await get_room_message(room)
        if msg:
            await msg.edit(embed=create_lobby_embed(room))

        save_rooms()

        await interaction.response.send_message(
            f"Bạn đã vào **{room['room_name']}** — đội {'Đỏ' if team=='teamA' else 'Xanh'} — lane **{ROLES[role]}**!",
            ephemeral=True
        )


    @discord.ui.button(label="Top", style=discord.ButtonStyle.danger, row=1)
    async def red_top(self, i, b): await self.pick(i, "teamA", "Top")

    @discord.ui.button(label="Rừng", style=discord.ButtonStyle.danger, row=1)
    async def red_jungle(self, i, b): await self.pick(i, "teamA", "Jungle")

    @discord.ui.button(label="Mid", style=discord.ButtonStyle.danger, row=1)
    async def red_mid(self, i, b): await self.pick(i, "teamA", "Mid")

    @discord.ui.button(label="ADC", style=discord.ButtonStyle.danger, row=1)
    async def red_adc(self, i, b): await self.pick(i, "teamA", "ADC")

    @discord.ui.button(label="Support", style=discord.ButtonStyle.danger, row=1)
    async def red_sup(self, i, b): await self.pick(i, "teamA", "Support")

    @discord.ui.button(label="Top", style=discord.ButtonStyle.primary, row=3)
    async def blue_top(self, i, b): await self.pick(i, "teamB", "Top")

    @discord.ui.button(label="Rừng", style=discord.ButtonStyle.primary, row=3)
    async def blue_jungle(self, i, b): await self.pick(i, "teamB", "Jungle")

    @discord.ui.button(label="Mid", style=discord.ButtonStyle.primary, row=3)
    async def blue_mid(self, i, b): await self.pick(i, "teamB", "Mid")

    @discord.ui.button(label="ADC", style=discord.ButtonStyle.primary, row=3)
    async def blue_adc(self, i, b): await self.pick(i, "teamB", "ADC")

    @discord.ui.button(label="Support", style=discord.ButtonStyle.primary, row=3)
    async def blue_sup(self, i, b): await self.pick(i, "teamB", "Support")

    # Hàng cuối: các nút chức năng (row 4)
    @discord.ui.button(label="🚪 Rời Phòng", style=discord.ButtonStyle.secondary, row=4)
    async def leave(self, interaction, button):
        room = rooms[self.room_id]
        user = interaction.user.id

        found = False
        for t in [room["teamA"], room["teamB"]]:
            for r in ROLES:
                if t[r] == user:
                    t[r] = None
                    found = True

        if not found:
            return await interaction.response.send_message("❌ Bạn không thuộc phòng này!", ephemeral=True)

        msg = await get_room_message(room)
        if msg:
            await msg.edit(embed=create_lobby_embed(room))

        save_rooms()
        await interaction.response.send_message("Bạn đã rời phòng 😢", ephemeral=True)

    @discord.ui.button(label="🗑️ Huỷ Phòng", style=discord.ButtonStyle.danger, row=4)
    async def delete_room(self, interaction, button):
        room = rooms[self.room_id]
        msg = await get_room_message(room)

        if msg:
            try:
                await msg.delete()
            except:
                try:
                    await msg.edit(content="🗑️ Phòng đã bị huỷ!", embed=None, view=None)
                except:
                    pass

        del rooms[self.room_id]
        save_rooms()

        await interaction.response.send_message("🗑️ Phòng đã bị huỷ!", ephemeral=True)

    @discord.ui.button(label="🎲 Random Giữ Role", style=discord.ButtonStyle.success, row=4)
    async def random_keep(self, interaction, button):
        room = rooms[self.room_id]
        do_random_keep(room)

        msg = await get_room_message(room)
        if msg:
            await msg.edit(embed=create_lobby_embed(room))

        save_rooms()
        await interaction.response.send_message("🎲 Random giữ role xong!", ephemeral=True)

    @discord.ui.button(label="🎲 Random All", style=discord.ButtonStyle.success, row=4)
    async def random_all(self, interaction, button):
        room = rooms[self.room_id]
        do_random_all(room)

        msg = await get_room_message(room)
        if msg:
            await msg.edit(embed=create_lobby_embed(room))

        save_rooms()
        await interaction.response.send_message("🎲 Random đội + role xong!", ephemeral=True)


# ============================
# COUNTDOWN + REMINDER
# ============================

@tasks.loop(seconds=30)
async def update_countdowns():
    now = int(datetime.now().timestamp())

    for rid, room in list(rooms.items()):
        ts = room.get("match_timestamp")
        if not ts:
            continue

        diff = ts - now
        minutes = diff // 60

        embed = create_lobby_embed(room)
        embed.description += (
            f"\n\n⏳ **Còn {minutes} phút**" if diff > 0 else "\n\n🔥 **Đã đến giờ trận!**"
        )

        msg = await get_room_message(room)
        if msg:
            try:
                await msg.edit(embed=embed)
            except:
                pass

        for m in [30, 15, 10, 5, 1]:
            if minutes == m and not room["reminded"][m]:
                room["reminded"][m] = True

                players = []
                for t in [room["teamA"], room["teamB"]]:
                    for r, u in t.items():
                        if u: players.append(f"<@{u}>")

                if players:
                    channel = bot.get_channel(room["channel"])
                    if channel:
                        await channel.send(f"⏰ Trận đấu bắt đầu trong **{m} phút**!\n{' '.join(players)}")

                save_rooms()

        if minutes == 0 and not room["reminded"][0]:
            room["reminded"][0] = True

            players = []
            for t in [room["teamA"], room["teamB"]]:
                for r, u in t.items():
                    if u: players.append(f"<@{u}>")

            if players:
                channel = bot.get_channel(room["channel"])
                if channel:
                    await channel.send(f"🔥 **Trận đấu bắt đầu!**\n{' '.join(players)}")

            save_rooms()


if __name__ == "__main__":
    import sys, os

    if os.getenv("RUN_TESTS") == "1":
        # simple simulation tests for room logic
        def print_room(room):
            print("Room:", room["room_name"])
            print("-- TeamA --")
            for r, u in room["teamA"].items():
                print(f"{r}:", u)
            print("-- TeamB --")
            for r, u in room["teamB"].items():
                print(f"{r}:", u)
            print("" + ("-"*40))

        rid = "test-room"
        rooms[rid] = {
            "channel": None,
            "room_name": "Test Room",
            "match_time": None,
            "match_timestamp": None,
            "reminded": {30: False, 15: False, 10: False, 5: False, 1: False, 0: False},
            "teamA": {r: None for r in ROLES},
            "teamB": {r: None for r in ROLES},
            "message_id": None,
        }

        # simulate one user in Support on teamB
        rooms[rid]["teamB"]["Support"] = 99999

        print("Initial state:")
        print_room(rooms[rid])

        print("Running 10 random_keep calls:")
        for i in range(10):
            do_random_keep(rooms[rid])
            print(f"After random_keep #{i+1}:")
            print_room(rooms[rid])

        # reset and test random_all + random_keep
        rooms[rid]["teamA"] = {r: None for r in ROLES}
        rooms[rid]["teamB"] = {r: None for r in ROLES}
        rooms[rid]["teamB"]["Support"] = 99999

        print("\nTesting random_all then random_keep multiple times:")
        for i in range(5):
            do_random_all(rooms[rid])
            print(f"After random_all #{i+1}:")
            print_room(rooms[rid])
            do_random_keep(rooms[rid])
            print(f"Then random_keep:")
            print_room(rooms[rid])

        sys.exit(0)
    else:
        bot.run(TOKEN)
