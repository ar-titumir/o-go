# My Agent — Day 1: Telegram + File Handler

A personal agent you own fully, built day by day.

## What works today

- Telegram bot (polling) — only YOU can talk to it
- Full file sandbox — create, read, modify, delete files in one directory
- Send/receive files and images via Telegram

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Create your `.env`

```bash
cp .env.example .env
```

Fill in:
| Variable | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) on Telegram |
| `TELEGRAM_ALLOWED_USER_ID` | Message [@userinfobot](https://t.me/userinfobot) |
| `AGENT_WORKSPACE_DIR` | Any absolute path you want the agent to own |

### 3. Run

```bash
python main.py
```

---

## Commands

| Command | What it does |
|---|---|
| `/start` | Show help |
| `/ls [subdir]` | List files in workspace |
| `/read <path>` | Print file contents |
| `/write <path>` | Next message → saved as file |
| `/rm <path>` | Delete a file |
| `/mkdir <path>` | Create a directory |
| `/info <path>` | File size, type, path |

Send any **document or image** → automatically saved to workspace.

---

## File structure

```
my-agent/
├── main.py               ← entry point
├── config/
│   └── settings.py       ← all config / env vars
├── core/
│   └── agent.py          ← central coordinator (grows each day)
├── gateway/
│   └── telegram/
│       ├── bot.py        ← Application setup + polling
│       ├── handlers.py   ← incoming message handlers
│       └── sender.py     ← outbound helpers
├── services/
│   └── file_handler.py   ← sandboxed file operations
├── utils/
│   └── logger.py         ← logging (stdout + file)
├── storage/              ← future: memory, db
├── logs/                 ← agent.log written here
└── workspace/            ← default sandbox dir (auto-created)
```

---

## What's coming next

- **Day 2** — AI brain: connect Claude / any LLM, plain chat works
- **Day 3** — Memory: agent remembers context across messages
- **Day 4** — Skills / commands: agent can run Python scripts on request
- **Day 5** — Scheduler: cron jobs, reminders
