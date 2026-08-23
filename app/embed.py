import discord
from app.storage import ROLES


def create_lobby_embed(room):
    def fmt(team):
        return "\n".join(
            f"{ROLES[r]} — {f'<@{u}>' if u else '— Trống —'}"
            for r, u in team.items()
        )

    embed = discord.Embed(
        title=f"🔥 {room['room_name']} 🔥",
        color=discord.Color.gold()
    )

    embed.description = (
        f"**⏰ Giờ thi đấu:** {room['match_time'] or 'Chưa đặt'}\n\n"
        f"## 🟥 Đội Đỏ\n{fmt(room['teamA'])}\n\n"
        f"## 🟦 Đội Xanh\n{fmt(room['teamB'])}"
    )

    embed.set_footer(text="Bot được làm bởi NAT!")
    return embed
