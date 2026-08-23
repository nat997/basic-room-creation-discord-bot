# League of Legends Custom Room Bot

Simple Discord bot to run 5v5 custom rooms for quick scrims.

Features
- Create a named room and post a lobby embed
- Players join lanes (Top/Jungle/Mid/ADC/Support) for Red/Blue teams
- `/set-time` to schedule a match and get countdown reminders
- `Random Giữ Role` (keep lanes, randomize sides) and `Random All` (random team+role assignment)

Requirements
- Python 3.10+
- Discord bot token in a `.env` file as `TOKEN=...`

Install

```powershell
pip install -r requirements.txt
```

Run

```powershell
python main.py
```

Development / Tests
- Simulated tests (no Discord connection):

```powershell
python tests/sim_tests.py
```

Project layout
- `main.py` — entrypoint and bot lifecycle
- `app/storage.py` — persistence and in-memory `rooms` state
- `app/embed.py` — embed builder
- `app/timeutils.py` — time parsing helpers
- `app/randomize.py` — deterministic/random assignment logic
- `app/views.py` — `LobbyView` and button handlers
- `app/commands.py` — command registration
- `tests/` — simulation scripts used during development

Notes for maintainers
- Keep logic testable: prefer pure functions in `app/randomize.py` and `app/timeutils.py`.
- Do not persist Discord message objects — store `channel` and `message_id` only.
- Handlers use fallbacks for interaction responses to avoid `Unknown interaction` errors.
- Views use per-room `asyncio.Lock` to avoid race conditions on rapid button presses.

Next improvements (non-blocking)
- Add pytest unit tests with deterministic RNG seeds
- Swap JSON persistence for SQLite or light DB if concurrent writes grow
- Add admin commands (rename room, archive/delete)

License
- No license specified. Add one before publishing.

Contributing
- Fork, add tests, open a PR. Small, testable changes preferred.