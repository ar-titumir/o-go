"""
gateway/telegram/sender.py
--------------------------
All outbound Telegram calls live here.
Handlers never call bot methods directly — they use these functions.
This makes it easy to mock in tests and to swap transports later.
"""

from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode

from utils import get_logger

log = get_logger(__name__)


async def send_text(bot: Bot, chat_id: int, text: str) -> None:
    """Send a plain text message. Falls back to plain text if Markdown fails."""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except Exception:
        # Markdown parse error — retry as plain text
        await bot.send_message(chat_id=chat_id, text=text)
    log.debug("send_text → %s: %.60s…", chat_id, text)


async def send_file(bot: Bot, chat_id: int, file_path: Path, caption: str = "") -> None:
    """Send any file as a Telegram document."""
    with file_path.open("rb") as fh:
        await bot.send_document(
            chat_id=chat_id,
            document=fh,
            filename=file_path.name,
            caption=caption or file_path.name,
        )
    log.info("send_file → %s: %s", chat_id, file_path.name)


async def send_image(bot: Bot, chat_id: int, file_path: Path, caption: str = "") -> None:
    """Send an image file as a Telegram photo."""
    with file_path.open("rb") as fh:
        await bot.send_photo(
            chat_id=chat_id,
            photo=fh,
            caption=caption or file_path.name,
        )
    log.info("send_image → %s: %s", chat_id, file_path.name)


async def send_error(bot: Bot, chat_id: int, error: str) -> None:
    """Send a formatted error notice."""
    await bot.send_message(chat_id=chat_id, text=f"⚠️ Error: {error}")
    log.warning("send_error → %s: %s", chat_id, error)
