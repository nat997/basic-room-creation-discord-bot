import main

rid = "test-room"
main.rooms[rid] = {
    "channel": None,
    "room_name": "Test Room",
    "match_time": None,
    "match_timestamp": None,
    "reminded": {30: False, 15: False, 10: False, 5: False, 1: False, 0: False},
    "teamA": {r: None for r in main.ROLES},
    "teamB": {r: None for r in main.ROLES},
    "message_id": None,
}

# simulate one user in Support on teamB
main.rooms[rid]["teamB"]["Support"] = 99999


def print_room(room):
    print("Room:", room["room_name"])
    print("-- TeamA --")
    for r, u in room["teamA"].items():
        print(f"{r}: {u}")
    print("-- TeamB --")
    for r, u in room["teamB"].items():
        print(f"{r}: {u}")
    print("" + ("-"*40))

print("Initial state:")
print_room(main.rooms[rid])

print("Running 10 random_keep calls:")
for i in range(10):
    main.do_random_keep(main.rooms[rid])
    print(f"After random_keep #{i+1}:")
    print_room(main.rooms[rid])

# reset and test random_all + random_keep
main.rooms[rid]["teamA"] = {r: None for r in main.ROLES}
main.rooms[rid]["teamB"] = {r: None for r in main.ROLES}
main.rooms[rid]["teamB"]["Support"] = 99999

print("\nTesting random_all then random_keep multiple times:")
for i in range(5):
    main.do_random_all(main.rooms[rid])
    print(f"After random_all #{i+1}:")
    print_room(main.rooms[rid])
    main.do_random_keep(main.rooms[rid])
    print(f"Then random_keep:")
    print_room(main.rooms[rid])
