#!/usr/bin/env python3
"""
Core automation engine - extracted from main.py
Can be used standalone or imported by the Telegram bot
"""

import aiohttp
import asyncio
import time
import random
from typing import Dict, List, Optional, Callable
from collections import deque
from dataclasses import dataclass

# Configuration
BASE_URL = "https://api.aistudy.uz/api/StudyAILms"
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


@dataclass
class UserProgress:
    """Data class for user progress tracking"""
    user_idx: int
    status: str
    lesson_id: Optional[int] = None
    progress: float = 0.0
    wait_time: int = 0
    course_name: str = ""


class AdaptiveTiming:
    def __init__(self, fast_mode: bool):
        self.fast_mode = fast_mode
        self.response_times = deque(maxlen=20)
        self.error_count = 0
        self.success_count = 0
        self.last_429_time = 0

        if fast_mode:
            self.min_sleep = 3
            self.max_sleep = 15
            self.between_lessons = 0.5
            self.between_courses = 2
            self.aggression = 1.5
        else:
            self.min_sleep = 10
            self.max_sleep = 60
            self.between_lessons = 3
            self.between_courses = 8
            self.aggression = 0.7

    def record_success(self, response_time: float):
        self.response_times.append(response_time)
        self.success_count += 1
        self.error_count = max(0, self.error_count - 1)
        if len(self.response_times) >= 5:
            avg = sum(self.response_times) / len(self.response_times)
            if avg < 0.5 and self.success_count > 10:
                self.min_sleep = max(1, self.min_sleep * 0.95)
                self.max_sleep = max(5, self.max_sleep * 0.95)

    def record_error(self, status_code: int):
        self.error_count += 1
        if status_code == 429:
            self.last_429_time = time.time()
            self.min_sleep = min(self.min_sleep * 1.5, 20)
            self.max_sleep = min(self.max_sleep * 1.3, 30)
            self.between_lessons *= 1.2
        elif status_code == 400:
            self.min_sleep = min(self.min_sleep * 1.1, 20)

    def get_sleep_time(self, base_time: float) -> float:
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 60:
            multiplier = 1.2
        else:
            error_rate = self.error_count / max(1, self.success_count)
            multiplier = 1.3 if error_rate > 0.1 else (1.1 if error_rate > 0.05 else self.aggression)
        sleep_time = max(self.min_sleep, min(base_time * multiplier, self.max_sleep))
        return sleep_time + random.uniform(-0.1, 0.1) * sleep_time

    def should_wait_after_429(self) -> int:
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 10:
            return 20 if self.fast_mode else 25
        return 10 if self.fast_mode else 15


class UserContext:
    def __init__(self, user_idx: int, token: str, fast_mode: bool, update_callback: Optional[Callable] = None):
        self.user_idx = user_idx
        self.token = token
        self.timing = AdaptiveTiming(fast_mode)
        self.session: aiohttp.ClientSession = None
        self.update_callback = update_callback  # Callback for progress updates
        self.current_course_name = ""
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": token,
            "Origin": "https://omp.aistudy.uz",
            "Referer": "https://omp.aistudy.uz/",
        }

    async def init_session(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def notify_progress(self, status: str, lesson_id: int = None, progress: float = 0.0, wait: int = 0):
        """Notify progress update via callback"""
        if self.update_callback:
            await self.update_callback(UserProgress(
                user_idx=self.user_idx,
                status=status,
                lesson_id=lesson_id,
                progress=progress,
                wait_time=wait,
                course_name=self.current_course_name
            ))


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
            await ctx.notify_progress(f"✓ {name[:30]}", lesson_id, 100.0, 0)
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

            base_sleep = time_increment * (0.3 if ctx.timing.fast_mode else 0.7)
            sleep_time = int(ctx.timing.get_sleep_time(base_sleep))

            # Real-time countdown with progress updates
            end_time = time.time() + sleep_time
            while True:
                remaining = int(end_time - time.time())
                if remaining <= 0:
                    break
                await ctx.notify_progress(f"⏳ {name[:30]}", lesson_id, target_percent, remaining)
                await asyncio.sleep(1)

            await ctx.notify_progress(f"📤 {name[:30]}", lesson_id, target_percent, 0)

            # POST with retries
            for retry in range(4):
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
                            wait = ctx.timing.should_wait_after_429() + retry * 2
                            await ctx.notify_progress(f"⚠️ 429 retry {retry+1}/3", lesson_id, target_percent, wait)
                            await asyncio.sleep(wait)
                        elif res.status == 400:
                            try:
                                err = await res.json()
                                if "already" in err.get("error", "").lower():
                                    break
                            except Exception:
                                pass
                            wait = 20 + retry * 2
                            await asyncio.sleep(wait)
                        else:
                            await asyncio.sleep(10 + retry * 2)
                except aiohttp.ClientError:
                    await asyncio.sleep(10 + retry * 2)

            current_percent = target_percent
            if target_percent < 100:
                await asyncio.sleep(ctx.timing.get_sleep_time(1))

        await ctx.notify_progress(f"✓ {name[:30]}", lesson_id, 100.0, 0)
        return True

    except Exception as e:
        await ctx.notify_progress(f"❌ {name[:20]}", lesson_id, 0, 0)
        return False


async def solve_quiz(ctx: UserContext, quiz_id: int, name: str) -> bool:
    try:
        await ctx.notify_progress(f"🧠 Quiz {name[:20]}", None, 0, 0)

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

        for retry in range(4):
            try:
                async with ctx.session.post(
                    f"{BASE_URL}/Quiz/CheckQuizAndSaveResult",
                    headers=ctx.headers,
                    json=payload,
                ) as res:
                    if res.status == 200:
                        await ctx.notify_progress(f"✓ Quiz {name[:20]}", None, 100.0, 0)
                        await asyncio.sleep(ctx.timing.get_sleep_time(2))
                        return True
                    wait = 15 + retry * 2
                    await asyncio.sleep(wait)
            except Exception:
                await asyncio.sleep(10 + retry * 2)

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


async def process_user(ctx: UserContext, cert_callback: Optional[Callable] = None):
    """
    Process a single user through all courses
    cert_callback: Optional callback when certificate is obtained (cert_id, full_name, user_idx)
    """
    try:
        await ctx.init_session()
        await ctx.notify_progress("Checking certificate...", None, 0, 0)

        cert = await check_certificate(ctx)
        if cert:
            cert_id = cert.get("id")
            full_name = cert.get("userFullName", "Unknown")
            await ctx.notify_progress(f"✅ CERT: {full_name}", None, 100.0, 0)
            if cert_callback:
                await cert_callback(cert_id, full_name, ctx.user_idx)
            return

        await ctx.notify_progress("Fetching courses...", None, 0, 0)
        courses = await get_all_courses(ctx)

        if not courses:
            await ctx.notify_progress("❌ No courses / expired", None, 0, 0)
            return

        for course in courses:
            try:
                course_id   = course["id"]
                course_name = course.get("courseName", {}).get("uz", f"Course {course_id}")
                ctx.current_course_name = course_name

                await ctx.notify_progress(f"▶ {course_name[:35]}", None, 0, 0)
                await start_course(ctx, course_id)
                await asyncio.sleep(ctx.timing.get_sleep_time(2))

                tree = await get_course_tree(ctx, course_id)
                for node in tree:
                    await process_tree_node(ctx, node)

                await asyncio.sleep(ctx.timing.get_sleep_time(3))
                cert = await check_certificate(ctx)
                if cert:
                    cert_id   = cert.get("id")
                    full_name = cert.get("userFullName", "Unknown")
                    await ctx.notify_progress(f"✅ CERT: {full_name}", None, 100.0, 0)
                    if cert_callback:
                        await cert_callback(cert_id, full_name, ctx.user_idx)
                    return

                await asyncio.sleep(ctx.timing.get_sleep_time(ctx.timing.between_courses))
            except Exception:
                pass

        cert = await check_certificate(ctx)
        if cert:
            cert_id   = cert.get("id")
            full_name = cert.get("userFullName", "Unknown")
            await ctx.notify_progress(f"✅ DONE: {full_name}", None, 100.0, 0)
            if cert_callback:
                await cert_callback(cert_id, full_name, ctx.user_idx)
        else:
            await ctx.notify_progress("❌ No certificate", None, 0, 0)

    except Exception as e:
        await ctx.notify_progress(f"❌ Fatal: {str(e)[:30]}", None, 0, 0)
    finally:
        await ctx.close_session()
