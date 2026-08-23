import main
import random
from collections import Counter


def print_room(room):
    print("Room:", room["room_name"])
    print("-- TeamA --")
    for r, u in room["teamA"].items():
        print(f"{r}: {u}")
    print("-- TeamB --")
    for r, u in room["teamB"].items():
        print(f"{r}: {u}")
    print("" + ("-"*40))


# Setup two rooms
r1 = "room-1"
r2 = "room-2"
main.rooms[r1] = {
    "channel": None,
    "room_name": "Alpha",
    "match_time": None,
    "match_timestamp": None,
    "reminded": {30: False, 15: False, 10: False, 5: False, 1: False, 0: False},
    "teamA": {r: None for r in main.ROLES},
    "teamB": {r: None for r in main.ROLES},
    "message_id": None,
}
main.rooms[r2] = {
    "channel": None,
    "room_name": "Beta",
    "match_time": None,
    "match_timestamp": None,
    "reminded": {30: False, 15: False, 10: False, 5: False, 1: False, 0: False},
    "teamA": {r: None for r in main.ROLES},
    "teamB": {r: None for r in main.ROLES},
    "message_id": None,
}

# Simulate joins: 8 users join room-1 in different roles
users = list(range(1001, 1010))
roles = list(main.ROLES.keys())
for i, uid in enumerate(users[:8]):
    role = roles[i % len(roles)]
    # alternate assign to teamA/teamB
    if i % 2 == 0:
        main.rooms[r1]["teamA"][role] = uid
    else:
        main.rooms[r1]["teamB"][role] = uid

print("Initial Room-1 state")
print_room(main.rooms[r1])

# Simulate leave: remove one user
leaver = users[2]
for t in [main.rooms[r1]["teamA"], main.rooms[r1]["teamB"]]:
    for role, uid in t.items():
        if uid == leaver:
            t[role] = None
            print(f"User {leaver} left (removed from {role})")

print_room(main.rooms[r1])

# Simulate multi-room membership: put user 1005 in room-2 as Mid
multi = 1005
main.rooms[r2]["teamA"]["Mid"] = multi
print(f"User {multi} is now also in room-2 Mid")
print_room(main.rooms[r2])

# Rapid presses test: single-player Support in room-2
uid = 999
main.rooms[r2]["teamA"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamB"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamB"]["Support"] = uid

counts = Counter()
N = 200
for i in range(N):
    main.do_random_keep(main.rooms[r2])
    # find where uid ended
    where = None
    for team in ("teamA", "teamB"):
        for role, u in main.rooms[r2][team].items():
            if u == uid:
                where = (team, role)
    counts[where] += 1

print(f"After {N} random_keep runs for single user {uid} (Support):")
print(counts)

# Rapid presses with multiple users in same role
main.rooms[r2]["teamA"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamB"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamA"]["Support"] = 2001
main.rooms[r2]["teamB"]["Support"] = 2002
main.rooms[r2]["teamA"]["Mid"] = 2003

counts_multi = Counter()
N = 200
for i in range(N):
    main.do_random_keep(main.rooms[r2])
    locs = []
    for team in ("teamA", "teamB"):
        for role, u in main.rooms[r2][team].items():
            if u:
                locs.append((team, role, u))
    # sort to create hashable summary
    locs.sort()
    counts_multi[tuple(locs)] += 1

print(f"After {N} random_keep runs for multi-users: distinct layouts: {len(counts_multi)}")
# show top 5 layouts
for layout, c in counts_multi.most_common(5):
    print(c, layout)

# Test rapid random_all effects
# Prepare 3 players
main.rooms[r2]["teamA"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamB"] = {r: None for r in main.ROLES}
main.rooms[r2]["teamA"]["Top"] = 3001
main.rooms[r2]["teamA"]["Mid"] = 3002
main.rooms[r2]["teamB"]["Support"] = 3003

counts_all = Counter()
N = 200
for i in range(N):
    main.do_random_all(main.rooms[r2])
    # record assignment summary (role->user mapping)
    mapping = tuple(sorted([(team, role, u) for team in ("teamA","teamB") for role,u in main.rooms[r2][team].items() if u]))
    counts_all[mapping] += 1

print(f"After {N} random_all runs: distinct mappings: {len(counts_all)}")
for m,c in counts_all.most_common(5):
    print(c)
