import random
from app.storage import ROLES


def do_random_keep(room):
    role_to_players = {r: [] for r in ROLES}
    for r in ROLES:
        if room["teamA"][r]: role_to_players[r].append(room["teamA"][r])
        if room["teamB"][r]: role_to_players[r].append(room["teamB"][r])

    room["teamA"] = {r: None for r in ROLES}
    room["teamB"] = {r: None for r in ROLES}

    for r, players in role_to_players.items():
        if not players:
            continue
        random.shuffle(players)
        start = random.choice([0, 1])
        for i, u in enumerate(players):
            if (i + start) % 2 == 0:
                room["teamA"][r] = u
            else:
                room["teamB"][r] = u


def do_random_all(room):
    players = []
    for t in [room["teamA"], room["teamB"]]:
        for r, u in t.items():
            if u:
                players.append(u)

    players = list(dict.fromkeys(players))
    random.shuffle(players)

    room["teamA"] = {r: None for r in ROLES}
    room["teamB"] = {r: None for r in ROLES}

    roles = list(ROLES.keys())
    slots = [("teamA", r) for r in roles] + [("teamB", r) for r in roles]
    random.shuffle(slots)

    for i, u in enumerate(players):
        if i >= len(slots):
            break
        team_key, role_key = slots[i]
        room[team_key][role_key] = u
