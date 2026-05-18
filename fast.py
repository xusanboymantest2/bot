#!/usr/bin/env python3
import aiohttp
import asyncio
import time
import sys
import random
from typing import Dict, List, Optional
from collections import deque

# Configuration
FAST_MODE = "--fast" in sys.argv or "-f" in sys.argv
LUDICROUS_MODE = "--ludicrous" in sys.argv or "-l" in sys.argv
sys.argv = [arg for arg in sys.argv if arg not in ["--fast", "-f", "--ludicrous", "-l"]]

if len(sys.argv) < 2:
    print("Usage:")
    print("  python3 main.py tokens.txt [--fast] [--ludicrous]")
    print("  python3 main.py 'Bearer TOKEN1' 'Bearer TOKEN2' [--fast] [--ludicrous]")
    print("\nModes:")
    print("  (none)      = SAFE    - slow, careful, polite")
    print("  --fast      = FAST⚡  - aggressive, minimal delays")
    print("  --ludicrous = INSANE🔥 - zero fucks given, maximum chaos")
    sys.exit(1)

# ── Token parsing ─────────────────────────────────────────────────────────────
TOKENS = []

def _extract_tokens(text: str):
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

mode_str = "INSANE🔥" if LUDICROUS_MODE else ("FAST⚡" if FAST_MODE else "SAFE🛡️")
print(f"[+] Loaded {len(TOKENS)} token(s). Starting in {mode_str} mode...")

BASE_URL = "https://api.aistudy.uz/api/StudyAILms"
TG_BOT_TOKEN = "8710650940:AAGinJwmYqcWN5J_yC2HZYTBQOpq2EgvTFg"
TG_CHAT_ID = 6588631008

PROGRESS_CHECKPOINTS = [20.11, 40.23, 80.44, 100.00]

QUIZZES_DB = {
    1: [
        {"quizQuestionId": 1, "answers": [{"answerId": 2, "state": True}]},
        {"quizQuestionId": 2, "answers": [{"answerId": 8, "state": True}]},
        {"quizQuestionId": 3, "answers": [{"answerId": 12, "state": True}]},
        {"quizQuestionId": 4, "answers": [{"answerId": 13, "state": True}]},
        {"quizQuestionId": 5, "answers": [{"answerId": 19, "state": True}]},
        {"quizQuestionId": 6, "answers": [{"answerId": 22, "state": True}]}
    ],
    2: [
        {"quizQuestionId": 7, "answers": [{"answerId": 26, "state": True}]},
        {"quizQuestionId": 8, "answers": [{"answerId": 29, "state": True}]},
        {"quizQuestionId": 9, "answers": [{"answerId": 35, "state": True}]},
        {"quizQuestionId": 10, "answers": [{"answerId": 37, "state": True}]},
        {"quizQuestionId": 11, "answers": [{"answerId": 44, "state": True}]},
        {"quizQuestionId": 12, "answers": [{"answerId": 48, "state": True}]}
    ],
    3: [
        {"quizQuestionId": 13, "answers": [{"answerId": 52, "state": True}]},
        {"quizQuestionId": 14, "answers": [{"answerId": 53, "state": True}]},
        {"quizQuestionId": 15, "answers": [{"answerId": 59, "state": True}]},
        {"quizQuestionId": 16, "answers": [{"answerId": 62, "state": True}]},
        {"quizQuestionId": 17, "answers": [{"answerId": 68, "state": True}]},
        {"quizQuestionId": 18, "answers": [{"answerId": 70, "state": True}]},
        {"quizQuestionId": 19, "answers": [{"answerId": 75, "state": True}]}
    ],
    4: [
        {"quizQuestionId": 20, "answers": [{"answerId": 77, "state": True}]},
        {"quizQuestionId": 21, "answers": [{"answerId": 82, "state": True}]},
        {"quizQuestionId": 22, "answers": [{"answerId": 86, "state": True}]},
        {"quizQuestionId": 23, "answers": [{"answerId": 90, "state": True}]},
        {"quizQuestionId": 24, "answers": [{"answerId": 95, "state": True}]},
        {"quizQuestionId": 25, "answers": [{"answerId": 100, "state": True}]},
        {"quizQuestionId": 26, "answers": [{"answerId": 101, "state": True}]}
    ],
    5: [
        {"quizQuestionId": 27, "answers": [{"answerId": 106, "state": True}]},
        {"quizQuestionId": 28, "answers": [{"answerId": 112, "state": True}]},
        {"quizQuestionId": 29, "answers": [{"answerId": 115, "state": True}]},
        {"quizQuestionId": 30, "answers": [{"answerId": 117, "state": True}]},
        {"quizQuestionId": 31, "answers": [{"answerId": 122, "state": True}]},
        {"quizQuestionId": 32, "answers": [{"answerId": 127, "state": True}]},
        {"quizQuestionId": 33, "answers": [{"answerId": 130, "state": True}]},
        {"quizQuestionId": 34, "answers": [{"answerId": 135, "state": True}]},
        {"quizQuestionId": 35, "answers": [{"answerId": 139, "state": True}]},
        {"quizQuestionId": 36, "answers": [{"answerId": 142, "state": True}]},
        {"quizQuestionId": 37, "answers": [{"answerId": 146, "state": True}]},
        {"quizQuestionId": 38, "answers": [{"answerId": 149, "state": True}]}
    ]
}


class AdaptiveTiming:
    def __init__(self, fast_mode: bool, ludicrous: bool):
        self.fast_mode = fast_mode
        self.ludicrous = ludicrous
        self.response_times = deque(maxlen=20)
        self.error_count = 0
        self.success_count = 0
        self.last_429_time = 0

        if ludicrous:
            # INSANE MODE - fuck around and find out
            self.min_sleep = 0.5
            self.max_sleep = 5
            self.between_lessons = 0.1
            self.between_courses = 0.5
            self.aggression = 2.5
            self.checkpoint_multiplier = 0.05  # 5% of video time
            self.retry_delay = 3
            self.max_retries = 2
        elif fast_mode:
            # FAST MODE - aggressive but not suicidal
            self.min_sleep = 2
            self.max_sleep = 10
            self.between_lessons = 0.3
            self.between_courses = 1
            self.aggression = 1.8
            self.checkpoint_multiplier = 0.15  # 15% of video time
            self.retry_delay = 5
            self.max_retries = 3
        else:
            # SAFE MODE - original conservative timings
            self.min_sleep = 10
            self.max_sleep = 60
            self.between_lessons = 3
            self.between_courses = 8
            self.aggression = 0.7
            self.checkpoint_multiplier = 0.7  # 70% of video time
            self.retry_delay = 10
            self.max_retries = 4

    def record_success(self, response_time: float):
        self.response_times.append(response_time)
        self.success_count += 1
        self.error_count = max(0, self.error_count - 1)
        
        # Adaptive speedup in ludicrous mode
        if self.ludicrous and len(self.response_times) >= 3:
            avg = sum(self.response_times) / len(self.response_times)
            if avg < 0.3 and self.success_count > 5:
                self.min_sleep = max(0.2, self.min_sleep * 0.9)
                self.max_sleep = max(2, self.max_sleep * 0.9)

    def record_error(self, status_code: int):
        self.error_count += 1
        if status_code == 429:
            self.last_429_time = time.time()
            if not self.ludicrous:
                self.min_sleep = min(self.min_sleep * 1.5, 20)
                self.max_sleep = min(self.max_sleep * 1.3, 30)
                self.between_lessons *= 1.2

    def get_sleep_time(self, base_time: float) -> float:
        if self.ludicrous:
            # In ludicrous mode, barely sleep at all
            return max(0.1, base_time * 0.1 + random.uniform(0, 0.2))
        
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 60:
            multiplier = 1.2
        else:
            error_rate = self.error_count / max(1, self.success_count)
            multiplier = 1.3 if error_rate > 0.1 else (1.1 if error_rate > 0.05 else self.aggression)
        
        sleep_time = max(self.min_sleep, min(base_time * multiplier, self.max_sleep))
        return sleep_time + random.uniform(-0.05, 0.05) * sleep_time

    def should_wait_after_429(self) -> int:
        if self.ludicrous:
            return random.randint(2, 5)  # Fuck it, short wait
        
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 10:
            return 20 if self.fast_mode else 25
        return 10 if self.fast_mode else 15


class StatusDisplay:
    HEADER_LINES = 3
    FOOTER_LINES = 1

    def __init__(self, num_users: int):
        self.num_users = num_users
        self.user_status: Dict[int, dict] = {
            i: {"status": "Initializing...", "lesson_id": None, "progress": 0.0, "wait": 0}
            for i in range(num_users)
        }
        self.lock = asyncio.Lock()
        self._ready = False

    def initial_render(self):
        mode = "INSANE🔥" if LUDICROUS_MODE else ("FAST⚡" if FAST_MODE else "SAFE🛡️")
        print("=" * 80)
        print(f"AI Study Multi-Account Automator | {self.num_users} Users | {mode}")
        print("=" * 80)
        for i in range(self.num_users):
            print(self._format_line(i))
        print("=" * 80)
        sys.stdout.flush()
        self._ready = True

    async def update_user(self, user_idx: int, status: str,
                          lesson_id: int = None, progress: float = 0.0, wait: int = 0):
        async with self.lock:
            self.user_status[user_idx] = {
                "status": status,
                "lesson_id": lesson_id,
                "progress": progress,
                "wait": wait,
            }
            if self._ready:
                self._write_line(user_idx)

    def _format_line(self, user_idx: int) -> str:
        d = self.user_status[user_idx]
        lesson_str = f"L{d['lesson_id']}" if d["lesson_id"] else "---"
        bar = self._progress_bar(d["progress"])
        wait_str = f"{d['wait']}s" if d["wait"] > 0 else "---"
        line = f"User[{user_idx}] | {lesson_str:6} | {bar} | Wait: {wait_str:5} | {d['status']}"
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


class UserContext:
    def __init__(self, user_idx: int, token: str):
        self.user_idx = user_idx
        self.token = token
        self.timing = AdaptiveTiming(FAST_MODE, LUDICROUS_MODE)
        self.session: aiohttp.ClientSession = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": token,
            "Origin": "https://omp.aistudy.uz",
            "Referer": "https://omp.aistudy.uz/",
        }
        # Connection pooling for max speed
        self.connector = aiohttp.TCPConnector(
            limit=50 if LUDICROUS_MODE else 20,
            ttl_dns_cache=300,
            force_close=False,
            enable_cleanup_closed=True
        )

    async def init_session(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=15 if LUDICROUS_MODE else 30),
            connector=self.connector
        )

    async def close_session(self):
        if self.session:
            await self.session.close()
        if self.connector:
            await self.connector.close()


async def send_telegram(cert_id: str, full_name: str, user_idx: int):
    try:
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        text = (f"✅ User[{user_idx}] Certificate Ready!\n\n"
                f"👤 {full_name}\n"
                f"🔗 https://omp.aistudy.uz/certificate?id={cert_id}")
        async with aiohttp.ClientSession() as s:
            await s.post(url, json={"chat_id": TG_CHAT_ID, "text": text})
    except Exception:
        pass


async def check_certificate(ctx: UserContext) -> Optional[Dict]:
    try:
        async with ctx.session.get(f"{BASE_URL}/Certificate/GetCertificateByUser",
                                   headers=ctx.headers) as res:
            if res.status == 200:
                data = await res.json()
                if data.get("statusCode") == 200 and data.get("result"):
                    return data["result"]
    except Exception:
        pass
    return None


async def get_lesson_duration(ctx: UserContext, lesson_id: int) -> int:
    try:
        t0 = time.time()
        async with ctx.session.get(f"{BASE_URL}/Lesson/GetLessonById?id={lesson_id}",
                                   headers=ctx.headers) as res:
            ctx.timing.record_success(time.time() - t0) if res.status == 200 else ctx.timing.record_error(res.status)
            if res.status == 200:
                data = await res.json()
                dur = data.get("result", {}).get("duration", {}).get("uz", "2:00")
                m, s = map(int, dur.split(":"))
                return m * 60 + s
    except Exception:
        pass
    return 120


async def watch_lesson_smart(ctx: UserContext, lesson_id: int, name: str,
                             current_percent: float = 0.0) -> bool:
    try:
        if current_percent >= 99.9:
            await status_display.update_user(ctx.user_idx, f"✓ {name[:30]}", lesson_id, 100.0, 0)
            return True

        duration = await get_lesson_duration(ctx, lesson_id)
        time_used = (current_percent / 100.0) * duration
        checkpoints = [cp for cp in PROGRESS_CHECKPOINTS if cp > current_percent]

        for target_percent in checkpoints:
            percent_delta = target_percent - current_percent
            time_increment = (percent_delta / 100.0) * duration

            time_used += time_increment

            payload = {
                "lessonId": lesson_id,
                "language": "uz",
                "percentJson": {
                    "uz": f"{target_percent:.2f}",
                    "ru": f"{target_percent:.2f}",
                    "en": f"{target_percent:.2f}",
                },
                "usedTime": round(time_used, 6),
            }

            # Sleep calculation based on mode
            base_sleep = time_increment * ctx.timing.checkpoint_multiplier
            sleep_time = int(ctx.timing.get_sleep_time(base_sleep))

            # Countdown only if sleep > 2 seconds (skip in ludicrous mode mostly)
            if sleep_time > 2:
                end_time = time.time() + sleep_time
                while True:
                    remaining = int(end_time - time.time())
                    if remaining <= 0:
                        break
                    await status_display.update_user(
                        ctx.user_idx, f"⏳ {name[:30]}", lesson_id, target_percent, remaining
                    )
                    await asyncio.sleep(1)
            else:
                await status_display.update_user(
                    ctx.user_idx, f"⏳ {name[:30]}", lesson_id, target_percent, sleep_time
                )
                await asyncio.sleep(sleep_time)

            await status_display.update_user(ctx.user_idx, f"📤 {name[:30]}", lesson_id, target_percent, 0)

            # POST with retries
            for retry in range(ctx.timing.max_retries):
                try:
                    t0 = time.time()
                    async with ctx.session.post(
                        f"{BASE_URL}/UserWatchStory/CreateOrUpdateLessonWatch",
                        headers=ctx.headers,
                        json=payload,
                    ) as res:
                        ctx.timing.record_success(time.time() - t0) if res.status == 200 else ctx.timing.record_error(res.status)
                        if res.status == 200:
                            break
                        elif res.status == 429:
                            wait = ctx.timing.should_wait_after_429()
                            await status_display.update_user(
                                ctx.user_idx, f"⚠️ 429 retry {retry+1}/{ctx.timing.max_retries}", 
                                lesson_id, target_percent, wait
                            )
                            await asyncio.sleep(wait)
                        elif res.status == 400:
                            try:
                                err = await res.json()
                                if "already" in err.get("error", "").lower():
                                    break
                            except Exception:
                                pass
                            await asyncio.sleep(ctx.timing.retry_delay)
                        else:
                            await asyncio.sleep(ctx.timing.retry_delay)
                except aiohttp.ClientError:
                    await asyncio.sleep(ctx.timing.retry_delay)

            current_percent = target_percent
            if target_percent < 100:
                await asyncio.sleep(ctx.timing.get_sleep_time(ctx.timing.between_lessons))

        await status_display.update_user(ctx.user_idx, f"✓ {name[:30]}", lesson_id, 100.0, 0)
        return True

    except Exception as e:
        await status_display.update_user(ctx.user_idx, f"❌ {name[:20]}", lesson_id, 0, 0)
        return False


async def solve_quiz(ctx: UserContext, quiz_id: int, name: str) -> bool:
    try:
        await status_display.update_user(ctx.user_idx, f"🧠 Quiz {name[:20]}", None, 0, 0)

        if quiz_id in QUIZZES_DB:
            answers = QUIZZES_DB[quiz_id]
        else:
            try:
                async with ctx.session.get(f"{BASE_URL}/Quiz/GetQuizById?id={quiz_id}",
                                           headers=ctx.headers) as res:
                    if res.status != 200:
                        return False
                    data = await res.json()
                    questions = data.get("result", {}).get("questions", [])
                    answers = [
                        {"quizQuestionId": q["id"],
                         "answers": [{"answerId": q["questionAnswers"][0]["id"], "state": True}]}
                        for q in questions
                    ]
            except Exception:
                return False

        payload = {"quizId": quiz_id, "quizQuestions": answers}

        for retry in range(ctx.timing.max_retries):
            try:
                async with ctx.session.post(
                    f"{BASE_URL}/Quiz/CheckQuizAndSaveResult",
                    headers=ctx.headers,
                    json=payload,
                ) as res:
                    if res.status == 200:
                        await status_display.update_user(ctx.user_idx, f"✓ Quiz {name[:20]}", None, 100.0, 0)
                        await asyncio.sleep(ctx.timing.get_sleep_time(0.5))
                        return True
                    await asyncio.sleep(ctx.timing.retry_delay)
            except Exception:
                await asyncio.sleep(ctx.timing.retry_delay)

        return False
    except Exception:
        return False


async def process_tree_node(ctx: UserContext, node: Dict):
    try:
        if node.get("status") == 2:
            return
        node_type = node.get("type")
        node_id   = node.get("id")
        name      = node.get("name", {}).get("uz", "Unknown")

        if node_type == 1:
            # Process children concurrently in ludicrous mode
            if LUDICROUS_MODE:
                tasks = [process_tree_node(ctx, child) for child in node.get("children", [])]
                await asyncio.gather(*tasks)
            else:
                for child in node.get("children", []):
                    await process_tree_node(ctx, child)
        elif node_type == 2:
            await watch_lesson_smart(ctx, node_id, name, node.get("percent", 0))
        elif node_type == 3:
            await solve_quiz(ctx, node_id, name)
    except Exception:
        pass


async def start_course(ctx: UserContext, course_id: int) -> bool:
    try:
        async with ctx.session.post(
            f"{BASE_URL}/Progress/StartCourseProgress?courseId={course_id}",
            headers=ctx.headers, json={},
        ) as res:
            if res.status == 200:
                ctx.timing.record_success(0)
                return True
    except Exception:
        pass
    return False


async def get_course_tree(ctx: UserContext, course_id: int) -> List[Dict]:
    try:
        async with ctx.session.get(
            f"{BASE_URL}/Progress/GetPrivateCourseContentTree?courseId={course_id}",
            headers=ctx.headers,
        ) as res:
            if res.status == 200:
                data = await res.json()
                return data.get("result", {}).get("children", [])
    except Exception:
        pass
    return []


async def get_all_courses(ctx: UserContext) -> List[Dict]:
    try:
        async with ctx.session.get(f"{BASE_URL}/Course/GetAllCourses",
                                   headers=ctx.headers) as res:
            if res.status == 200:
                data = await res.json()
                return data.get("result", {}).get("items", [])
    except Exception:
        pass
    return []


async def process_user(user_idx: int, token: str):
    ctx = UserContext(user_idx, token)
    MAX_ATTEMPTS = 3
    start_time = time.time()
    TIMEOUT_SECONDS = 3600 * 2  # Optional 2-hour timeout per user

    try:
        await ctx.init_session()
        
        for attempt in range(1, MAX_ATTEMPTS + 1):
            # 1. Initial Certificate Check
            await status_display.update_user(user_idx, f"Check Attempt {attempt}/{MAX_ATTEMPTS}", None, 0, 0)
            cert = await check_certificate(ctx)
            if cert:
                cert_id = cert.get("id")
                full_name = cert.get("userFullName", "Unknown")
                await status_display.update_user(user_idx, f"✅ CERT: {full_name}", None, 100.0, 0)
                await send_telegram(cert_id, full_name, user_idx)
                return

            # 2. Fetch and Process Courses
            await status_display.update_user(user_idx, f"Fetching (Try {attempt})", None, 0, 0)
            courses = await get_all_courses(ctx)

            if not courses:
                await status_display.update_user(user_idx, "❌ No courses found", None, 0, 0)
                # If no courses are even visible, retrying might not help, 
                # but we'll wait and try again anyway just in case of API lag.
            else:
                for course in courses:
                    course_id = course["id"]
                    course_name = course.get("courseName", {}).get("uz", f"Course {course_id}")

                    await status_display.update_user(user_idx, f"▶ Attempt {attempt}: {course_name[:30]}", None, 0, 0)
                    await start_course(ctx, course_id)
                    
                    tree = await get_course_tree(ctx, course_id)
                    for node in tree:
                        await process_tree_node(ctx, node)
                    
                    await asyncio.sleep(ctx.timing.get_sleep_time(2))

            # 3. Final Check for this attempt
            cert = await check_certificate(ctx)
            if cert:
                cert_id = cert.get("id")
                full_name = cert.get("userFullName", "Unknown")
                await status_display.update_user(user_idx, f"✅ CERT: {full_name}", None, 100.0, 0)
                await send_telegram(cert_id, full_name, user_idx)
                return

            # 4. Preparation for next attempt
            if attempt < MAX_ATTEMPTS:
                wait_time = 30 if FAST_MODE else 60
                await status_display.update_user(user_idx, f"Retrying attempt {attempt+1}...", None, 0, wait_time)
                await asyncio.sleep(wait_time)
            
            # Global Timeout Safety
            if (time.time() - start_time) > TIMEOUT_SECONDS:
                await status_display.update_user(user_idx, "❌ Global Timeout reached", None, 0, 0)
                break

        await status_display.update_user(user_idx, "❌ Failed after 3 attempts", None, 0, 0)

    except Exception as e:
        await status_display.update_user(user_idx, f"❌ Fatal: {str(e)[:20]}", None, 0, 0)
    finally:
        await ctx.close_session()

async def main():
    global status_display
    status_display = StatusDisplay(len(TOKENS))
    status_display.initial_render()

    tasks = [process_user(i, token) for i, token in enumerate(TOKENS)]
    await asyncio.gather(*tasks)

    print(f"\n✅ All {len(TOKENS)} users processed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user")
    except Exception as e:
        print(f"[!] Fatal: {e}")