import logging
import os
import re

import duckdb
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from .constants import COMMANDS, CREDIT_CARDS
from .sql import load_sql

logging.basicConfig(level=logging.INFO)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


class SpendForm(StatesGroup):
    username = State()
    amount = State()
    month_year = State()


class ResetForm(StatesGroup):
    confirm = State()


async def init_db():
    """Initialize DB tables on startup"""
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        con.execute(load_sql("create_table.sql"))


def get_card_keyboard():
    """Generate inline keyboard with credit card options"""
    keyboard = []
    row = []
    for i, (code, name) in enumerate(CREDIT_CARDS.items()):
        row.append(InlineKeyboardButton(text=name, callback_data=f"card_{code}"))
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.message(Command("help"))
async def help_command(message: Message):
    help_text = "📋 Available Commands:\n\n"
    for cmd, desc in COMMANDS.items():
        help_text += f"/{cmd} - {desc}\n"
    await message.answer(help_text)


@router.message(Command("start"))
async def start(message: Message):
    username = message.from_user.username or "Anonymous"
    help_text = f"👋 Hi @{username}!\n\n📋 Commands:\n\n"
    for cmd, desc in COMMANDS.items():
        help_text += f"/{cmd} - {desc}\n"
    await message.answer(help_text)


@router.message(Command("add"))
async def add_spend(message: Message, state: FSMContext):
    await state.set_state(SpendForm.username)
    await message.answer("💳 Select your credit card:", reply_markup=get_card_keyboard())


@router.callback_query(F.data.startswith("card_"))
async def process_card_selection(callback: CallbackQuery, state: FSMContext):
    card_code = callback.data.split("_")[1]
    card_name = CREDIT_CARDS.get(card_code, "Unknown")
    username = callback.from_user.username or "Anonymous"

    await state.update_data(
        card=card_name,
        username=username,  # ✅ Auto Telegram username
    )
    await state.set_state(SpendForm.amount)
    await callback.message.edit_text(
        f"✅ Card: {card_name}\n👤 You: @{username}\n\n💰 Enter amount (e.g. 123.45):"
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Cancelled.", reply_markup=None)
    await callback.answer()


@router.message(SpendForm.amount)
async def process_amount(message: Message, state: FSMContext):
    if not re.match(r"^\d+(\.\d{2})?$", message.text):
        return await message.answer("❌ Invalid amount. Enter like 123.45:")
    await state.update_data(amount=float(message.text))
    await state.set_state(SpendForm.month_year)
    await message.answer("📅 Enter YYYY-MM (e.g. 2026-01):")


@router.message(SpendForm.month_year)
async def process_month_year(message: Message, state: FSMContext):
    if not re.match(r"^\d{4}-\d{2}$", message.text):
        return await message.answer("❌ Invalid format. Enter YYYY-MM:")
    data = await state.get_data()
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        con.execute(
            load_sql("insert_spend.sql"),
            [message.from_user.id, data["username"], data["card"], data["amount"], message.text],
        )
    await state.clear()
    await message.answer(
        f"✅ Added: {data['username']} | {data['card']} | ${data['amount']:.2f} | {message.text}"
    )


@router.message(Command("export"))
async def export_data(message: Message):
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        df = con.execute(load_sql("export_all.sql")).df()
    if df.empty:
        return await message.answer("No data yet.")

    csv_path = "export.csv"
    excel_path = "export.xlsx"
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)

    await message.answer_document(FSInputFile(csv_path), caption="📊 CSV export")
    await message.answer_document(FSInputFile(excel_path), caption="📈 Excel export")

    os.remove(csv_path)
    os.remove(excel_path)


@router.message(Command("stats"))
async def stats(message: Message):
    user_id = message.from_user.id
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        result = con.execute(load_sql("stats_user.sql"), [user_id]).df()
    if result.empty:
        return await message.answer("No spends recorded for you yet.")

    username = message.from_user.username or "Anonymous"
    stats_text = f"💰 @{username} Monthly Stats:\n\n"

    for _, row in result.iterrows():
        stats_text += f"📅 {row['month_year']}\n"
        stats_text += f"💵 Total: ${row['total']:.2f}\n"
        stats_text += f"📊 Txns: {int(row['transactions'])} | Avg: ${row['avg_spend']:.2f}\n\n"
    await message.answer(stats_text)


@router.message(Command("list"))
async def list_spends(message: Message):
    user_id = message.from_user.id
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        result = con.execute(load_sql("list_user.sql"), [user_id]).df()
    if result.empty:
        return await message.answer("No spends recorded for you yet.")

    list_text = "📝 Your Recent Spends (Last 10):\n\n"
    for _, row in result.iterrows():
        list_text += f"🕒 {row['created_at'].strftime('%Y-%m-%d %H:%M')}\n"
        list_text += f"💳 {row['card']} - ${row['amount']:.2f} ({row['month_year']})\n\n"
    await message.answer(list_text)


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel(message: Message, state: FSMContext):
    current = await state.get_state()
    if current:
        await state.clear()
        await message.answer("❌ Cancelled.", reply_markup=ReplyKeyboardRemove())


@router.message(Command("reset"))
async def reset_start(message: Message, state: FSMContext):
    username = message.from_user.username or "Anonymous"
    await state.set_state(ResetForm.confirm)
    await message.answer(
        f"⚠️  PERMANENT RESET\n\n"
        f"This will delete *ALL* your spend data!\n\n"
        f"@{username} - Are you sure? Reply <code>Y</code>",
        parse_mode="HTML",
    )


@router.message(ResetForm.confirm)
async def reset_confirm(message: Message, state: FSMContext):
    if message.text.strip().upper() != "Y":
        await state.clear()
        return await message.answer("✅ Reset cancelled. Your data is safe.")

    user_id = message.from_user.id
    sql = load_sql("delete_user_data.sql")
    with duckdb.connect(os.getenv("DB_PATH")) as con:
        result = con.execute(sql, [user_id])
        deleted = result.rowcount

    username = message.from_user.username or "Anonymous"
    await state.clear()
    await message.answer(
        f"🗑️ Reset complete!\n\nDeleted {deleted} records for @{username}\nStart fresh with /add"
    )


async def start_polling(token: str):
    await init_db()
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await bot.set_my_commands(
        [
            BotCommand(command=command, description=description)
            for command, description in COMMANDS.items()
        ]
    )
    await dp.start_polling(bot)
