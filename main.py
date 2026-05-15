#!/usr/bin/env python3
import asyncio
import sys
import re
from typing import Dict
from automation_core import UserContext, process_user, UserProgress
from alive import keep_alive

# ── Configuration ─────────────────────────────────────────────────────────────
FAST_MODE = "--fast" in sys.argv or "-f" in sys.argv
sys.argv = [arg for arg in sys.argv if arg not in ["--fast", "-f"]]

if len(sys.argv) < 2:
    print("Usage:")
    print("  python3 main.py tokens.txt [--fast]        ← recommended")
    print("  python3 main.py 'Bearer TOKEN1' 'Bearer TOKEN2' [--fast]")
    print("\nTelegram Bot:")
    print("  python3 telegram_bot.py                    ← start bot")
    sys.exit(1)

# ── Token parsing ─────────────────────────────────────────────────────────────
TOKENS = []

def _extract_tokens(text: str):
    """Pull every 'Bearer <jwt>' from a block of text."""
    import re
    return ["Bearer " + t for t in re.findall(r'Bearer\s+(\S+)', text)]

first_arg = sys.argv[1]
if first_arg.endswith(".txt") or (not first_arg.startswith("Bearer") and "\n" not in first_arg):
    try:
        with open(first_arg) as f:
            TOKENS = _extract_tokens(f.read())
    except FileNotFoundError:
        print(f"[!] File not found: {first_arg}")
        sys.exit(1)
else:
    TOKENS = _extract_tokens(" ".join(sys.argv[1:]))

if not TOKENS:
    print("[!] No valid Bearer tokens found.")
    sys.exit(1)

print(f"[+] Loaded {len(TOKENS)} token(s). Starting in {'FAST' if FAST_MODE else 'SAFE'} mode...")

# Telegram notification settings
TG_BOT_TOKEN = "8710650940:AAGinJwmYqcWN5J_yC2HZYTBQOpq2EgvTFg"
TG_CHAT_ID = 6588631008


# ─── In-place status display ──────────────────────────────────────────────────
class StatusDisplay:
    """
    Prints a fixed-height dashboard once, then uses ANSI cursor positioning
    to update individual user lines in-place — no screen clearing, no flicker.
    All users update simultaneously since each writes only its own row.
    """

    HEADER_LINES = 3   # top ===, title, bottom ===
    FOOTER_LINES = 1   # bottom ===

    def __init__(self, num_users: int):
        self.num_users = num_users
        self.user_status: Dict[int, UserProgress] = {
            i: UserProgress(i, "Initializing...", None, 0.0, 0)
            for i in range(num_users)
        }
        self.lock = asyncio.Lock()
        self._ready = False

    def initial_render(self):
        """Call once before starting tasks to draw the static frame."""
        mode = "FAST⚡" if FAST_MODE else "SAFE🛡️"
        print("=" * 80)
        print(f"AI Study Multi-Account Automator | {self.num_users} Users | {mode}")
        print("=" * 80)
        for i in range(self.num_users):
            print(self._format_line(i))
        print("=" * 80)
        sys.stdout.flush()
        self._ready = True

    async def update_user(self, progress: UserProgress):
        async with self.lock:
            self.user_status[progress.user_idx] = progress
            if self._ready:
                self._write_line(progress.user_idx)

    def _format_line(self, user_idx: int) -> str:
        d = self.user_status[user_idx]
        lesson_str = f"L{d.lesson_id}" if d.lesson_id else "---"
        bar = self._progress_bar(d.progress)
        wait_str = f"{d.wait_time}s" if d.wait_time > 0 else "---"
        line = f"User[{user_idx}] | {lesson_str:6} | {bar} | Wait: {wait_str:5} | {d.status}"
        return f"{line:<79}"

    @staticmethod
    def _progress_bar(progress: float, width: int = 20) -> str:
        filled = int(width * progress / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {progress:5.1f}%"

    def _write_line(self, user_idx: int):
        lines_up = (self.num_users - user_idx) + self.FOOTER_LINES
        line = self._format_line(user_idx)
        sys.stdout.write(f"\033[{lines_up}A\r{line}\033[{lines_up}B\r")
        sys.stdout.flush()


status_display: StatusDisplay = None


async def send_telegram(cert_id: str, full_name: str, user_idx: int):
    """Send telegram notification about certificate"""
    try:
        import aiohttp
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        text = (f"✅ User[{user_idx}] Certificate Ready!\n\n"
                f"👤 {full_name}\n"
                f"🔗 https://omp.aistudy.uz/certificate?id={cert_id}")
        async with aiohttp.ClientSession() as s:
            await s.post(url, json={"chat_id": TG_CHAT_ID, "text": text})
    except Exception:
        pass


async def process_user_cli(user_idx: int, token: str):
    """Process user with CLI display"""
    global status_display
    
    # Create update callback for status display
    async def update_callback(progress: UserProgress):
        await status_display.update_user(progress)
    
    # Create certificate callback
    async def cert_callback(cert_id: str, full_name: str, idx: int):
        await send_telegram(cert_id, full_name, idx)
    
    # Create context
    ctx = UserContext(user_idx, token, FAST_MODE, update_callback)
    
    # Run automation
    await process_user(ctx, cert_callback)


async def recursive_action():
    """
    Core action that creates a task of itself to prevent sleeping.
    """
    global status_display
    
    # Run all users simultaneously
    tasks = [process_user_cli(i, token) for i, token in enumerate(TOKENS)]
    await asyncio.gather(*tasks)
    
    # Cycle delay before restarting (adjust as needed)
    await asyncio.sleep(60)
    
    # Self-calling logic: Schedule next run on the event loop
    asyncio.create_task(recursive_action())


async def main():
    global status_display
    
    # 1. Start the Flask server in a background thread
    keep_alive()

    # 2. Setup the UI
    status_display = StatusDisplay(len(TOKENS))
    status_display.initial_render()

    # 3. Start the recursive processing loop
    await recursive_action()

    # 4. Final safety net to keep the event loop alive
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[!] Fatal: {e}")
