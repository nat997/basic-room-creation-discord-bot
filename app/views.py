import discord
from app.storage import rooms, save_rooms, get_room_message, ROLES, get_room_lock
from app.embed import create_lobby_embed
from app.randomize import do_random_keep, do_random_all


class LobbyView(discord.ui.View):
    def __init__(self, room_id):
        super().__init__(timeout=None)
        self.room_id = room_id

    async def pick(self, interaction, team, role):
        room = rooms[self.room_id]
        lock = get_room_lock(self.room_id)
        user = interaction.user.id

        async with lock:
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

    # bottom row
    @discord.ui.button(label="🚪 Rời Phòng", style=discord.ButtonStyle.secondary, row=4)
    async def leave(self, interaction, button):
        room = rooms[self.room_id]
        user = interaction.user.id
        lock = get_room_lock(self.room_id)

        found = False
        async with lock:
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
        lock = get_room_lock(self.room_id)

        async with lock:
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
        lock = get_room_lock(self.room_id)
        async with lock:
            do_random_keep(room)

            msg = await get_room_message(room)
            if msg:
                await msg.edit(embed=create_lobby_embed(room))

            save_rooms()

        await interaction.response.send_message("🎲 Random giữ role xong!", ephemeral=True)

    @discord.ui.button(label="🎲 Random All", style=discord.ButtonStyle.success, row=4)
    async def random_all(self, interaction, button):
        room = rooms[self.room_id]
        lock = get_room_lock(self.room_id)
        async with lock:
            do_random_all(room)

            msg = await get_room_message(room)
            if msg:
                await msg.edit(embed=create_lobby_embed(room))

            save_rooms()

        await interaction.response.send_message("🎲 Random đội + role xong!", ephemeral=True)
