# Credit Card Spend Tracker Bot

A simple Telegram bot for tracking credit card spending, storing monthly notes, and exporting personal spend data.

Built with Python, aiogram, and DuckDB.

## Features

- Add spend entries with card, amount, and month.
- Add monthly comments or notes.
- View monthly spend statistics.
- List recent transactions.
- Export data to CSV and Excel.
- Back up the local database.
- Delete recent records or reset all personal data.

## Commands

- `/start` - Show the welcome message.
- `/help` - Show available commands.
- `/add` - Add a spend entry.
- `/comment` - Add a monthly comment.
- `/stats` - View monthly stats.
- `/list` - Show recent spend records.
- `/export` - Export data as CSV and Excel.
- `/backup` - Create a database backup.
- `/delete` - Delete recent spend records.
- `/reset` - Remove all your stored data.
- `/cancel` - Cancel the current action.

## Stack

- Python
- [aiogram 3](https://docs.aiogram.dev/en/latest/)
- DuckDB
- Pandas

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sienlonglim/expense-tracker.git
cd expense-tracker
```

### 2. Create a virtual environment with uv

```bash
uv venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies with uv

```bash
uv sync
```

### 4. Configure environment variables

Create a `.env` file:

```env
BOT_TOKEN=<your_telegram_bot_token>
DB_PATH=data/<your_db_name>.db # or md:<your_motherduck_db>
motherduck_token=<your_motherduck_token> # Only required if using MotherDuck
```

## Run

Start the bot:

```bash
python main.py
```
