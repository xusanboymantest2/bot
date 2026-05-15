#!/usr/bin/env python3
"""
Telegram Bot for AI Study Automation
Features:
- Real-time streaming progress updates (every second)
- Multi-user parallel execution
- Live dashboard view
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Optional
from alive import keep_alive
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from automation_core import UserContext, process_user, UserProgress
from config import BOT_TOKEN, ADMIN_IDS

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot initialization
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Global state
active_sessions: Dict[int, dict] = {}  # chat_id -> {contexts, tasks, message_id}


class BotStates(StatesGroup):
    waiting_tokens = State()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def parse_tokens(text: str) -> list:
    """Extract Bearer tokens from text"""
    return ["Bearer " + t for t in re.findall(r'Bearer\s+(\S+)', text)]


def format_dashboard(contexts: Dict[int, UserContext], progresses: Dict[int, UserProgress]) -> str:
    """Format multi-user dashboard"""
    mode = "FAST⚡" if contexts and contexts[0].timing.fast_mode else "SAFE🛡️"
    
    lines = [
        f"🤖 **AI Study Automation** | {len(contexts)} Users | {mode}",
        f"⏰ {datetime.now().strftime('%H:%M:%S')}",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ""
    ]
    
    for idx in sorted(contexts.keys()):
        prog = progresses.get(idx)
        if prog:
            # Progress bar
            bar_len = 15
            filled = int(bar_len * prog.progress / 100)
            bar = "█" * filled + "░" * (bar_len - filled)
            
            # Status line
            lesson_str = f"L{prog.lesson_id}" if prog.lesson_id else "---"
            wait_str = f"⏱{prog.wait_time}s" if prog.wait_time > 0 else ""
            
            lines.append(f"`User[{idx}]` {lesson_str:6} {bar} {prog.progress:5.1f}%")
            lines.append(f"└─ {prog.status[:35]} {wait_str}")
            
            if prog.course_name:
                lines.append(f"   📚 {prog.course_name[:30]}")
            
            lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


async def stream_updates(chat_id: int, contexts: Dict[int, UserContext]):
    """
    Stream real-time updates to Telegram
    Updates message every second with current progress
    """
    session = active_sessions.get(chat_id)
    if not session:
        return
    
    message_id = session.get('message_id')
    progresses: Dict[int, UserProgress] = {}
    last_text = ""
    
    # Initialize progress tracking
    for idx in contexts:
        progresses[idx] = UserProgress(idx, "Initializing...", None, 0.0, 0)
    
    # Update callback for automation core
    async def update_callback(progress: UserProgress):
        progresses[progress.user_idx] = progress
    
    # Set callback for all contexts
    for ctx in contexts.values():
        ctx.update_callback = update_callback
    
    try:
        while True:
            # Check if all tasks completed
            if all(t.done() for t in session['tasks']):
                break
            
            # Format dashboard
            current_text = format_dashboard(contexts, progresses)
            
            # Update only if changed (reduce API calls but still frequent)
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
                    
                except Exception as e:
                    if "message is not modified" not in str(e):
                        logger.error(f"Update error: {e}")
            
            # Update every 1 second for real-time feel
            await asyncio.sleep(1)
    
    except asyncio.CancelledError:
        logger.info(f"Stream cancelled for chat {chat_id}")
    except Exception as e:
        logger.error(f"Stream error: {e}")
    finally:
        # Final update
        try:
            final_text = format_dashboard(contexts, progresses)
            final_text += "\n\n✅ **Automation Complete!**"
            
            if message_id:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=final_text,
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Final update error: {e}")


async def certificate_callback(cert_id: str, full_name: str, user_idx: int, chat_id: int):
    """Send certificate notification"""
    try:
        text = (
            f"🎉 **Certificate Obtained!**\n\n"
            f"👤 User [{user_idx}]: {full_name}\n"
            f"🔗 [View Certificate](https://omp.aistudy.uz/certificate?id={cert_id})"
        )
        await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Cert notification error: {e}")


async def run_automation(chat_id: int, tokens: list, fast_mode: bool):
    """Run automation for all users in parallel"""
    # Create contexts
    contexts = {
        i: UserContext(i, token, fast_mode)
        for i, token in enumerate(tokens)
    }
    
    # Create certificate callback wrapper
    async def cert_cb(cert_id, full_name, user_idx):
        await certificate_callback(cert_id, full_name, user_idx, chat_id)
    
    # Start processing tasks (all run in parallel)
    tasks = [
        asyncio.create_task(process_user(ctx, cert_cb))
        for ctx in contexts.values()
    ]
    
    # Store session
    active_sessions[chat_id] = {
        'contexts': contexts,
        'tasks': tasks,
        'message_id': None
    }
    
    # Start streaming updates
    stream_task = asyncio.create_task(stream_updates(chat_id, contexts))
    
    try:
        # Wait for all users to complete
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"Automation error: {e}")
    finally:
        # Stop streaming
        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass
        
        # Cleanup
        if chat_id in active_sessions:
            del active_sessions[chat_id]


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Start command"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied. Contact admin.")
        return
    
    await message.answer(
        "🤖 **AI Study Automation Bot**\n\n"
        "**Quick Start:**\n"
        "Send me your Bearer tokens (one per line or space-separated)\n\n"
        "**Commands:**\n"
        "• /run - Start automation\n"
        "• /status - Check status\n"
        "• /stop - Stop running task\n"
        "• /help - Help\n\n"
        "**Features:**\n"
        "✓ Real-time progress streaming\n"
        "✓ Multi-user parallel execution\n"
        "✓ SAFE and FAST modes\n"
        "✓ Auto certificate detection",
        parse_mode="Markdown"
    )


@dp.message(Command("run"))
async def cmd_run(message: types.Message, state: FSMContext):
    """Start automation"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
    
    if message.chat.id in active_sessions:
        await message.answer("⚠️ Already running. Use /stop first.")
        return
    
    await message.answer(
        "📝 **Send your Bearer tokens:**\n\n"
        "**Format options:**\n"
        "```\n"
        "Bearer token1\n"
        "Bearer token2\n"
        "```\n"
        "Or:\n"
        "```\n"
        "Bearer token1 Bearer token2\n"
        "```\n\n"
        "You can also upload a .txt file\n\n"
        "Add `--fast` for fast mode",
        parse_mode="Markdown"
    )
    await state.set_state(BotStates.waiting_tokens)


@dp.message(BotStates.waiting_tokens, F.document)
async def handle_file(message: types.Message, state: FSMContext):
    """Handle token file upload"""
    try:
        file = await bot.get_file(message.document.file_id)
        file_content = await bot.download_file(file.file_path)
        text = file_content.read().decode('utf-8')
        
        tokens = parse_tokens(text)
        
        if not tokens:
            await message.answer("❌ No valid tokens found in file")
            return
        
        fast_mode = "--fast" in text or "-f" in text
        
        await message.answer(
            f"✅ Loaded {len(tokens)} token(s)\n"
            f"Mode: {'FAST⚡' if fast_mode else 'SAFE🛡️'}\n\n"
            f"🚀 Starting automation..."
        )
        
        await state.clear()
        
        # Start automation
        await run_automation(message.chat.id, tokens, fast_mode)
        
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
        await state.clear()


@dp.message(BotStates.waiting_tokens)
async def handle_tokens(message: types.Message, state: FSMContext):
    """Handle token text input"""
    text = message.text
    
    tokens = parse_tokens(text)
    
    if not tokens:
        await message.answer("❌ No valid Bearer tokens found")
        return
    
    fast_mode = "--fast" in text or "-f" in text
    
    await message.answer(
        f"✅ Loaded {len(tokens)} token(s)\n"
        f"Mode: {'FAST⚡' if fast_mode else 'SAFE🛡️'}\n\n"
        f"🚀 Starting automation..."
    )
    
    await state.clear()
    
    # Start automation
    await run_automation(message.chat.id, tokens, fast_mode)


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    """Stop automation"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
    
    chat_id = message.chat.id
    
    if chat_id in active_sessions:
        session = active_sessions[chat_id]
        
        # Cancel all tasks
        for task in session['tasks']:
            task.cancel()
        
        del active_sessions[chat_id]
        await message.answer("⏹️ Stopped")
    else:
        await message.answer("ℹ️ No active automation")


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    """Check status"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied")
        return
    
    chat_id = message.chat.id
    
    if chat_id in active_sessions:
        session = active_sessions[chat_id]
        num_users = len(session['contexts'])
        completed = sum(1 for t in session['tasks'] if t.done())
        
        await message.answer(
            f"📊 **Status**\n\n"
            f"👥 Users: {num_users}\n"
            f"✅ Completed: {completed}/{num_users}\n"
            f"🏃 Running: {num_users - completed}"
        )
    else:
        await message.answer("ℹ️ No active automation")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Help command"""
    await message.answer(
        "📖 **AI Study Bot Help**\n\n"
        "**Usage:**\n"
        "1. Send /run\n"
        "2. Send your Bearer tokens\n"
        "3. Watch real-time progress\n\n"
        "**Token Format:**\n"
        "`Bearer <your_token_here>`\n\n"
        "**Modes:**\n"
        "• Default (SAFE) - Slow, careful\n"
        "• --fast - Faster, aggressive\n\n"
        "**Features:**\n"
        "• Updates every 1 second\n"
        "• All users run in parallel\n"
        "• Auto certificate detection\n"
        "• Progress bars & countdown\n\n"
        "**Commands:**\n"
        "/run - Start automation\n"
        "/stop - Stop automation\n"
        "/status - Check status\n"
        "/help - This message",
        parse_mode="Markdown"
    )


async def main():
    """Bot entry point"""
    logger.info("🤖 Starting AI Study Bot...")
    logger.info(f"📱 Admins: {ADMIN_IDS}")
    
    try:
        # 1. Start the Flask server for Render
        print("[+] Starting Keep-Alive server...")
        keep_alive()

        # 2. Start the Bot Polling
        logging.info("🤖 Starting AI Study Bot...")
        bot = Bot(token="YOUR_BOT_TOKEN")
        dp = Dispatcher()
    
        # Add your handlers here
        # dp.include_router(your_router)

        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
