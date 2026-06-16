"""
gateway/telegram/bot.py
-----------------------
Build and return a fully-configured telegram Application.
main.py calls run() to start the bot.
"""

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN
from utils import get_logger
from .handlers import (
    cmd_start,
    cmd_ls,
    cmd_read,
    cmd_write,
    cmd_rm,
    cmd_mkdir,
    cmd_info,
    handle_text,
    handle_document,
    handle_photo,
)

log = get_logger(__name__)


def build_app() -> Application:
    """Create and wire up the Telegram Application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # ── Commands ───────────────────────────────────────────────────────────────
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("ls",     cmd_ls))
    app.add_handler(CommandHandler("read",   cmd_read))
    app.add_handler(CommandHandler("write",  cmd_write))
    app.add_handler(CommandHandler("rm",     cmd_rm))
    app.add_handler(CommandHandler("mkdir",  cmd_mkdir))
    app.add_handler(CommandHandler("info",   cmd_info))

    # ── Media ──────────────────────────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO,        handle_photo))

    # ── Plain text (must be last) ──────────────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Telegram handlers registered.")
    return app


def run() -> None:
    """Build the app and start polling (blocking)."""
    log.info("Starting Telegram bot (polling)…")
    app = build_app()
    app.run_polling(drop_pending_updates=True)
