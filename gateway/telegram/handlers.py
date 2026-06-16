"""
gateway/telegram/handlers.py
-----------------------------
All incoming Telegram update handlers.

Commands available today
------------------------
/start          — greeting
/ls [subdir]    — list files in workspace (or subdir)
/read <path>    — print file contents
/write <path>   — next message becomes the file content
/rm <path>      — delete a file
/mkdir <path>   — create a directory
/info <path>    — file metadata

Sending a document/photo → saved into workspace automatically.
Replying to a bot document message → re-sends that file.
"""

from pathlib import Path

from telegram import Update, Message
from telegram.ext import ContextTypes

import services as fs
from config import AGENT_WORKSPACE_DIR, TELEGRAM_ALLOWED_USER_ID
from utils import get_logger
from .sender import send_text, send_file, send_image, send_error

log = get_logger(__name__)

# Tracks users who issued /write — next plain message becomes file content
_pending_write: dict[int, str] = {}   # user_id → target relative path


# ── Auth guard ─────────────────────────────────────────────────────────────────

def _is_allowed(update: Update) -> bool:
    return update.effective_user is not None and \
           update.effective_user.id == TELEGRAM_ALLOWED_USER_ID


async def _auth_fail(update: Update) -> None:
    log.warning("Unauthorized access attempt from user %s", update.effective_user)
    await update.message.reply_text("🚫 Not authorized.")


# ── Command handlers ───────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)
    await update.message.reply_text(
        "👋 Agent online.\n\n"
        "Commands:\n"
        "/ls [subdir]      — list files\n"
        "/read <path>      — read file\n"
        "/write <path>     — write file (send content next)\n"
        "/rm <path>        — delete file\n"
        "/mkdir <path>     — create directory\n"
        "/info <path>      — file info\n\n"
        "Send any file/image → it will be saved to workspace."
    )


async def cmd_ls(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    subdir = " ".join(context.args) if context.args else "."
    try:
        files = fs.list_files(subdir)
        if not files:
            reply = f"📂 `{subdir}` is empty."
        else:
            listing = "\n".join(f"  {f}" for f in files)
            reply = f"📂 `{subdir}`:\n```\n{listing}\n```"
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


async def cmd_read(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    if not context.args:
        await update.message.reply_text("Usage: /read <relative_path>")
        return

    rel_path = " ".join(context.args)
    try:
        content = fs.read_file(rel_path)
        # Telegram message limit is 4096 chars
        if len(content) > 3800:
            # Send as file if too large
            tmp = AGENT_WORKSPACE_DIR / rel_path
            await send_file(update.get_bot(), update.effective_chat.id, tmp,
                            caption=f"Contents of {rel_path}")
        else:
            await update.message.reply_text(
                f"📄 `{rel_path}`:\n```\n{content}\n```",
                parse_mode="Markdown",
            )
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


async def cmd_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    if not context.args:
        await update.message.reply_text("Usage: /write <relative_path>")
        return

    rel_path = " ".join(context.args)
    _pending_write[update.effective_user.id] = rel_path
    await update.message.reply_text(
        f"✏️ Ready. Send the content for `{rel_path}` now.",
        parse_mode="Markdown",
    )


async def cmd_rm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    if not context.args:
        await update.message.reply_text("Usage: /rm <relative_path>")
        return

    rel_path = " ".join(context.args)
    try:
        fs.delete_file(rel_path)
        await update.message.reply_text(f"🗑️ Deleted `{rel_path}`.", parse_mode="Markdown")
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


async def cmd_mkdir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    if not context.args:
        await update.message.reply_text("Usage: /mkdir <relative_path>")
        return

    rel_path = " ".join(context.args)
    try:
        fs.make_dir(rel_path)
        await update.message.reply_text(f"📁 Created `{rel_path}`.", parse_mode="Markdown")
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


async def cmd_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    if not context.args:
        await update.message.reply_text("Usage: /info <relative_path>")
        return

    rel_path = " ".join(context.args)
    try:
        info = fs.file_info(rel_path)
        lines = "\n".join(f"  {k}: {v}" for k, v in info.items())
        await update.message.reply_text(f"ℹ️ File info:\n```\n{lines}\n```",
                                        parse_mode="Markdown")
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


# ── Plain text handler (also handles pending /write content) ───────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_allowed(update):
        return await _auth_fail(update)

    user_id = update.effective_user.id
    text = update.message.text or ""

    # If user previously issued /write, this message is the file content
    if user_id in _pending_write:
        rel_path = _pending_write.pop(user_id)
        try:
            fs.write_file(rel_path, text)
            await update.message.reply_text(
                f"✅ Saved to `{rel_path}`.", parse_mode="Markdown"
            )
        except Exception as e:
            await send_error(update.get_bot(), update.effective_chat.id, str(e))
        return

    # Default: echo back (will be replaced by AI response in a later day)
    await update.message.reply_text(f"📨 Received: {text}")


# ── File / photo handlers ──────────────────────────────────────────────────────

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save any incoming document into the workspace."""
    if not _is_allowed(update):
        return await _auth_fail(update)

    doc = update.message.document
    file_name = doc.file_name or f"file_{doc.file_id}"

    try:
        tg_file = await context.bot.get_file(doc.file_id)
        data = await tg_file.download_as_bytearray()
        saved = fs.save_bytes(file_name, bytes(data))
        await update.message.reply_text(
            f"💾 Saved `{file_name}` ({len(data):,} bytes).", parse_mode="Markdown"
        )
        log.info("Received document: %s → %s", file_name, saved)
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save the highest-resolution version of an incoming photo."""
    if not _is_allowed(update):
        return await _auth_fail(update)

    # photos arrive as a list; last = best quality
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    file_name = f"{caption.strip() or photo.file_id}.jpg"

    try:
        tg_file = await context.bot.get_file(photo.file_id)
        data = await tg_file.download_as_bytearray()
        saved = fs.save_bytes(file_name, bytes(data))
        await update.message.reply_text(
            f"🖼️ Saved `{file_name}` ({len(data):,} bytes).", parse_mode="Markdown"
        )
        log.info("Received photo: %s → %s", file_name, saved)
    except Exception as e:
        await send_error(update.get_bot(), update.effective_chat.id, str(e))
