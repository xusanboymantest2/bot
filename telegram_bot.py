#!/usr/bin/env python3
"""
Telegram Bot for AI Study Automation
Features:
- Real-time streaming progress updates (Configurable Interval)
- Multi-user parallel execution
- High-Water Mark Progress Tracking (No backward jumps)
- Anti-Flood Protection (TelegramRetryAfter handling)
- Live dashboard view
"""

import asyncio
import logging
import re
import os
from datetime import datetime
from typing import Dict, Optional

# Third-party imports
from alive import keep_alive
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramRetryAfter, TelegramForbiddenError

# Project-specific imports
from automation_core import UserContext, process_user, UserProgress
from config import BOT_TOKEN, ADMIN_IDS

# ================= CONFIGURATION =================
# Set this to 2 or 3 seconds to avoid Telegram Flood Limits
# 3 seconds is recommended for stability in 2026
DASHBOARD_UPDATE_INTERVAL = 2
MAX_STATUS_LENGTH = 35
PROGRESS_BAR_LENGTH = 15
# =================================================

# Logging Configuration
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot initialization
TOKEN = os.getenv("TOKEN") or BOT_TOKEN
if not TOKEN:
    logging.error("BOT_TOKEN is missing! Add it to Environment Variables.")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Global state management
# chat_id -> {
#    'contexts': Dict[int, UserContext], 
#    'tasks': List[asyncio.Task], 
#    'message_id': int,
#    'max_progress': Dict[int, float]  <-- Tracks the highest % reached
# }
active_sessions: Dict[int, dict] = {}


class BotStates(StatesGroup):
    """FSM States for the bot"""
    waiting_tokens = State()


def is_admin(user_id: int) -> bool:
    """Check if a user is in the admin list"""
    return user_id in ADMIN_IDS


def parse_tokens(text: str) -> list:
    """Extract Bearer tokens from text using Regex"""
    return ["Bearer " + t for t in re.findall(r'Bearer\s+(\S+)', text)]


def format_dashboard(contexts: Dict[int, UserContext], progresses: Dict[int, UserProgress]) -> str:
    """
    Constructs the visual dashboard for Telegram.
    Uses the progress values currently stored in the stream_updates loop.
    """
    # Determine mode based on first user (assuming all share same mode in a session)
    try:
        sample_ctx = next(iter(contexts.values()))
        mode = "FAST⚡" if sample_ctx.timing.fast_mode else "SAFE🛡️"
    except (StopIteration, AttributeError):
        mode = "UNKNOWN ❓"
    
    lines = [
        f"🤖 **AI Study Automation** | {len(contexts)} Users | {mode}",
        f"⏰ {datetime.now().strftime('%H:%M:%S')}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    for idx in sorted(contexts.keys()):
        prog = progresses.get(idx)
        if prog:
            # Progress bar calculation
            # Clamp percentage between 0 and 100 for visual safety
            clamped_pct = max(0.0, min(100.0, prog.progress))
            filled = int(PROGRESS_BAR_LENGTH * clamped_pct / 100)
            bar = "█" * filled + "░" * (PROGRESS_BAR_LENGTH - filled)
            
            # Metadata formatting
            lesson_str = f"L{prog.lesson_id}" if prog.lesson_id else "---"
            wait_str = f"⏱{prog.wait_time}s" if prog.wait_time > 0 else ""
            
            # Construct entry
            lines.append(f"`User[{idx}]` {lesson_str:6} {bar} {clamped_pct:5.1f}%")
            lines.append(f"└─ {prog.status[:MAX_STATUS_LENGTH]} {wait_str}")
            
            if hasattr(prog, 'course_name') and prog.course_name:
                lines.append(f"   📚 {prog.course_name[:30]}")
            
            lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


async def stream_updates(chat_id: int, contexts: Dict[int, UserContext]):
    """
    Handles real-time updates to the Telegram message.
    Implements Forward-Only progress logic (High-Water Mark).
    """
    session = active_sessions.get(chat_id)
    if not session:
        logger.warning(f"Attempted to stream updates for inactive session: {chat_id}")
        return
    
    message_id = session.get('message_id')
    progresses: Dict[int, UserProgress] = {}
    max_progress_tracker: Dict[int, float] = {} # Persistent high-water mark
    last_text = ""
    
    # Initialize trackers for each user index
    for idx in contexts:
        progresses[idx] = UserProgress(idx, "Initializing...", None, 0.0, 0)
        max_progress_tracker[idx] = 0.0
    
    # Define the callback that the backend automation will call
    async def update_callback(new_data: UserProgress):
        idx = new_data.user_idx
        
        # LOGIC: Ensure progress never jumps backwards
        # If new_data reports 20% but we already hit 60%, stick to 60%
        if idx in max_progress_tracker:
            if new_data.progress < max_progress_tracker[idx]:
                new_data.progress = max_progress_tracker[idx]
            else:
                max_progress_tracker[idx] = new_data.progress
        
        progresses[idx] = new_data
    
    # Attach callback to all active contexts
    for ctx in contexts.values():
        ctx.update_callback = update_callback
    
    try:
        while True:
            # Termination condition: All automation tasks are finished
            if all(t.done() for t in session['tasks']):
                logger.info(f"All tasks for {chat_id} completed. Closing stream.")
                break
            
            current_text = format_dashboard(contexts, progresses)
            
            # Only attempt edit if the text actually changed to save API quota
            if current_text != last_text:
                try:
                    if message_id:
                        await bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=current_text,
                            parse_mode="Markdown"
                        )
                    else:
                        msg = await bot.send_message(
                            chat_id=chat_id,
                            text=current_text,
                            parse_mode="Markdown"
                        )
                        session['message_id'] = msg.message_id
                        message_id = msg.message_id
                    
                    last_text = current_text

                except TelegramRetryAfter as e:
                    # Specific handling for flood limits: Wait exactly what Telegram says
                    logger.warning(f"Rate limited on chat {chat_id}. Sleeping {e.retry_after}s")
                    await asyncio.sleep(e.retry_after)
                    continue # Try again after sleep
                except Exception as e:
                    if "message is not modified" not in str(e):
                        logger.error(f"Stream update error in chat {chat_id}: {e}")
            
            # The throttle: Control how often we hit the Telegram API
            await asyncio.sleep(DASHBOARD_UPDATE_INTERVAL)
    
    except asyncio.CancelledError:
        logger.info(f"Streaming task for {chat_id} was cancelled.")
    except Exception as e:
        logger.exception(f"Unexpected stream error for {chat_id}: {e}")
    finally:
        # Final Dashboard state (mark as complete)
        try:
            final_text = format_dashboard(contexts, progresses)
            final_text += "\n\n✅ **Automation Process Complete!**"
            
            if message_id:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=final_text,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Final dashboard update failed: {e}")


async def certificate_callback(cert_id: str, full_name: str, user_idx: int, chat_id: int):
    """Sends certificate links as they are detected by the backend"""
    try:
        text = (
            f"🎉 **Certificate Obtained!**\n\n"
            f"👤 User [{user_idx}]: {full_name}\n"
            f"🔗 [View Certificate](https://omp.aistudy.uz/certificate?id={cert_id})"
        )
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
        logger.info(f"Certificate sent for user {user_idx} in chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send certificate notification: {e}")


async def run_automation(chat_id: int, tokens: list, fast_mode: bool):
    """Entry point for starting parallel automation runs"""
    # 1. Prepare contexts
    contexts = {
        i: UserContext(i, token, fast_mode)
        for i, token in enumerate(tokens)
    }
    
    # 2. Wrapper for the cert callback
    async def cert_cb_wrapper(cid, name, uidx):
        await certificate_callback(cid, name, uidx, chat_id)
    
    # 3. Spin up processing tasks for every user concurrently
    tasks = [
        asyncio.create_task(process_user(ctx, cert_cb_wrapper))
        for ctx in contexts.values()
    ]
    
    # 4. Save to session storage
    active_sessions[chat_id] = {
        'contexts': contexts,
        'tasks': tasks,
        'message_id': None
    }
    
    # 5. Launch the UI streamer
    stream_task = asyncio.create_task(stream_updates(chat_id, contexts))
    
    try:
        # Wait for all background automation tasks to finish
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Core automation task failed: {e}")
    finally:
        # Ensure the UI stream is cleaned up
        if not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup session data
        if chat_id in active_sessions:
            del active_sessions[chat_id]


# --- TELEGRAM HANDLERS ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied. Unauthorized User.")
        return
    
    welcome_text = (
        "🤖 **AI Study Automation Bot v2.0**\n\n"
        "**Usage:**\n"
        "Send your Bearer tokens to begin. You can send multiple tokens per message or upload a file.\n\n"
        "**Available Commands:**\n"
        "• /run - Input tokens & start\n"
        "• /status - View current session metrics\n"
        "• /stop - Force stop all active tasks\n"
        "• /help - Display usage guide\n\n"
        "**System Settings:**\n"
        f"Update Rate: {DASHBOARD_UPDATE_INTERVAL}s\n"
        "Parallel Engine: Enabled"
    )
    await message.answer(welcome_text, parse_mode="Markdown")


@dp.message(Command("run"))
async def cmd_run(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    
    if message.chat.id in active_sessions:
        await message.answer("⚠️ An automation session is already active. Stop it first using /stop.")
        return
    
    instructions = (
        "📝 **Automation Setup**\n\n"
        "Please provide your Bearer tokens.\n"
        "Format: `Bearer <token>`\n\n"
        "💡 *Tip: Add `--fast` anywhere in your message to enable High-Speed mode.*"
    )
    await message.answer(instructions, parse_mode="Markdown")
    await state.set_state(BotStates.waiting_tokens)


@dp.message(BotStates.waiting_tokens, F.document)
async def handle_file_input(message: types.Message, state: FSMContext):
    try:
        file = await bot.get_file(message.document.file_id)
        file_content = await bot.download_file(file.file_path)
        raw_text = file_content.read().decode('utf-8')
        
        tokens = parse_tokens(raw_text)
        if not tokens:
            await message.answer("❌ Error: No valid Bearer tokens detected in the file.")
            return
        
        fast_mode = "--fast" in raw_text or "-f" in raw_text
        await message.answer(f"✅ Loaded {len(tokens)} token(s). Initializing engine...")
        
        await state.clear()
        await run_automation(message.chat.id, tokens, fast_mode)
        
    except Exception as e:
        logger.exception("File handling failed")
        await message.answer(f"❌ Critical Error processing file: {e}")
        await state.clear()


@dp.message(BotStates.waiting_tokens)
async def handle_text_input(message: types.Message, state: FSMContext):
    tokens = parse_tokens(message.text)
    
    if not tokens:
        await message.answer("❌ Error: No valid tokens provided. Send tokens starting with 'Bearer'.")
        return
    
    fast_mode = "--fast" in message.text or "-f" in message.text
    await message.answer(f"✅ Received {len(tokens)} token(s). Starting...")
    
    await state.clear()
    await run_automation(message.chat.id, tokens, fast_mode)


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    if not is_admin(message.from_user.id): return
    
    chat_id = message.chat.id
    if chat_id in active_sessions:
        session = active_sessions[chat_id]
        for task in session['tasks']:
            task.cancel()
        
        await message.answer("⏹️ **Stop Command Received.** All tasks have been terminated.")
        # Cleanup is handled by the finally block in run_automation
    else:
        await message.answer("ℹ️ No active automation found for this chat.")


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    if not is_admin(message.from_user.id): return
    
    chat_id = message.chat.id
    if chat_id in active_sessions:
        session = active_sessions[chat_id]
        total = len(session['contexts'])
        done = sum(1 for t in session['tasks'] if t.done())
        
        await message.answer(
            f"📊 **Engine Status**\n\n"
            f"• Users: {total}\n"
            f"• Progress: {done}/{total} complete\n"
            f"• Threads: {total - done} active"
        )
    else:
        await message.answer("ℹ️ Engine is currently idle.")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 **Command Reference**\n\n"
        "1. **/run** -> Paste tokens or upload a .txt file.\n"
        "2. **Tokens** -> Must be in `Bearer <hash>` format.\n"
        "3. **Fast Mode** -> Append `--fast` to your token list.\n"
        "4. **/stop** -> Immediately kills all background threads.\n"
        "5. **/status** -> Check how many users are finished.\n\n"
        "⚠️ **Note:** The dashboard updates every few seconds to prevent Telegram rate limits."
    )
    await message.answer(help_text, parse_mode="Markdown")


async def main():
    """Bot initialization and main loop"""
    logger.info("Initializing system...")
    
    try:
        # Start the keep-alive web server (standard for Render/Heroku deployments)
        logger.info("Starting web server...")
        keep_alive()

        # Begin Telegram polling
        logger.info(f"Bot starting. Authorized Admins: {ADMIN_IDS}")
        await dp.start_polling(bot)
        
    except (TelegramForbiddenError, Exception) as e:
        logger.critical(f"Critical failure in bot main loop: {e}")
    finally:
        await bot.session.close()
        logger.info("System shutdown complete.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Manual shutdown triggered by user.")
