#!/usr/bin/env python3
import requests
import time
import sys
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import deque

# Configuration
FAST_MODE = "--fast" in sys.argv or "-f" in sys.argv

# Remove flags from argv
sys.argv = [arg for arg in sys.argv if arg not in ["--fast", "-f"]]

if len(sys.argv) < 2:
    print("Usage: python3 main.py Bearer YOUR_TOKEN [--fast]")
    print("  --fast, -f : Fast mode (adaptive, higher risk)")
    sys.exit(1)

TOKEN = " ".join(sys.argv[1:])
BASE_URL = "https://api.aistudy.uz/api/StudyAILms"
TG_BOT_TOKEN = "8710650940:AAGinJwmYqcWN5J_yC2HZYTBQOpq2EgvTFg"
TG_CHAT_ID = 6588631008

# Adaptive timing system
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
            avg_response = sum(self.response_times) / len(self.response_times)
            if avg_response < 0.5 and self.success_count > 10:
                self.min_sleep = max(1, self.min_sleep * 0.95)
                self.max_sleep = max(5, self.max_sleep * 0.95)
    
    def record_error(self, status_code: int):
        self.error_count += 1
        
        if status_code == 429:
            self.last_429_time = time.time()
            self.min_sleep *= 1.5
            self.max_sleep *= 1.3
            self.between_lessons *= 1.2
            print(f"\n    [!] Rate limit hit - backing off (min={self.min_sleep:.1f}s)")
        elif status_code == 400:
            self.min_sleep *= 1.1
            self.error_count += 0.5
        
        self.min_sleep = min(self.min_sleep, 30)
        self.max_sleep = min(self.max_sleep, 120)
    
    def get_sleep_time(self, base_time: float) -> float:
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 60:
            multiplier = 1.5
        else:
            error_rate = self.error_count / max(1, self.success_count)
            if error_rate > 0.1:
                multiplier = 1.3
            elif error_rate > 0.05:
                multiplier = 1.1
            else:
                multiplier = self.aggression
        
        sleep_time = base_time * multiplier
        sleep_time = max(self.min_sleep, min(sleep_time, self.max_sleep))
        
        jitter = random.uniform(-0.1, 0.1) * sleep_time
        return sleep_time + jitter
    
    def should_wait_after_429(self) -> int:
        time_since_429 = time.time() - self.last_429_time
        if time_since_429 < 10:
            return 30 if self.fast_mode else 45
        return 15 if self.fast_mode else 25

timing = AdaptiveTiming(FAST_MODE)

PROGRESS_CHECKPOINTS = [20.11, 40.23, 80.44, 100.00]

if FAST_MODE:
    print("[!] FAST MODE + ADAPTIVE TIMING - Estimated: 30-50 minutes")
else:
    print("[*] SAFE MODE + ADAPTIVE TIMING - Estimated: 1.5-2 hours")

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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Authorization": TOKEN,
    "Origin": "https://omp.aistudy.uz",
    "Referer": "https://omp.aistudy.uz/"
}

def countdown(seconds: int, prefix: str = ""):
    """Real-time countdown on same line"""
    for remaining in range(int(seconds), 0, -1):
        print(f"\r{prefix}[⏰] Waiting: {remaining}s...", end='', flush=True)
        time.sleep(1)
    print(f"\r{prefix}[⏰] Waiting: Done!     ", flush=True)

class ProgressTracker:
    def __init__(self):
        self.total_lessons = 0
        self.completed_lessons = 0
        self.total_quizzes = 0
        self.completed_quizzes = 0
        self.start_time = time.time()
        
    def update_totals(self, lessons: int, quizzes: int):
        self.total_lessons += lessons
        self.total_quizzes += quizzes
        
    def lesson_done(self):
        self.completed_lessons += 1
        self._print_progress()
        
    def quiz_done(self):
        self.completed_quizzes += 1
        self._print_progress()
        
    def _print_progress(self):
        elapsed = time.time() - self.start_time
        total_items = self.total_lessons + self.total_quizzes
        completed_items = self.completed_lessons + self.completed_quizzes
        
        if total_items == 0:
            return
            
        progress_pct = (completed_items / total_items) * 100
        
        if completed_items > 0:
            avg_time_per_item = elapsed / completed_items
            remaining_items = total_items - completed_items
            eta_seconds = avg_time_per_item * remaining_items
            eta = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta = "calculating..."
        
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        speed_mode = "AGGRESSIVE" if timing.min_sleep < 5 else "CAREFUL" if timing.min_sleep > 15 else "BALANCED"
        
        print(f"\n{'='*60}")
        print(f"Progress: {completed_items}/{total_items} ({progress_pct:.1f}%)")
        print(f"Lessons: {self.completed_lessons}/{self.total_lessons} | Quizzes: {self.completed_quizzes}/{self.total_quizzes}")
        print(f"Elapsed: {elapsed_str} | ETA: {eta}")
        print(f"Speed: {speed_mode} (sleep: {timing.min_sleep:.1f}-{timing.max_sleep:.1f}s)")
        print(f"Stats: {timing.success_count} ok / {timing.error_count} err")
        print(f"{'='*60}\n")

tracker = ProgressTracker()

def send_telegram(cert_id: str, full_name: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    text = f"✅ Certificate Ready!\n\n👤 {full_name}\n🔗 https://omp.aistudy.uz/certificate?id={cert_id}"
    
    try:
        requests.post(url, json={"chat_id": TG_CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def check_certificate() -> Optional[Dict]:
    try:
        res = requests.get(f"{BASE_URL}/Certificate/GetCertificateByUser", headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get('statusCode') == 200 and data.get('result'):
                return data['result']
    except:
        pass
    return None

def get_lesson_duration(lesson_id: int) -> int:
    try:
        start = time.time()
        res = requests.get(f"{BASE_URL}/Lesson/GetLessonById?id={lesson_id}", headers=headers, timeout=10)
        response_time = time.time() - start
        
        if res.status_code == 200:
            timing.record_success(response_time)
            data = res.json()
            if data.get('result') and data['result'].get('duration'):
                duration_str = data['result']['duration'].get('uz', '2:00')
                parts = duration_str.split(':')
                if len(parts) == 2:
                    minutes, seconds = int(parts[0]), int(parts[1])
                    return (minutes * 60) + seconds
        else:
            timing.record_error(res.status_code)
    except:
        pass
    return 120

def watch_lesson_smart(lesson_id: int, name: str, current_percent: float = 0) -> bool:
    """Watch lesson with retry logic and real-time countdown"""
    
    if current_percent >= 99.9:
        print(f"    [✓] Lesson {lesson_id} already completed")
        tracker.lesson_done()
        return True
    
    duration = get_lesson_duration(lesson_id)
    print(f"    [*] Watching: {name} ({duration}s)")
    
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
                "en": f"{target_percent:.2f}"
            },
            "usedTime": round(time_used, 6)
        }
        
        # Calculate adaptive sleep time
        base_sleep = time_increment * (0.3 if FAST_MODE else 0.7)
        sleep_time = timing.get_sleep_time(base_sleep)
        
        print(f"        [⏳] {target_percent:.2f}%:", end=' ', flush=True)
        
        # Countdown before request
        for remaining in range(int(sleep_time), 0, -1):
            print(f"\r        [⏳] {target_percent:.2f}%: {remaining}s...", end='', flush=True)
            time.sleep(1)
        
        print(f"\r        [⏳] {target_percent:.2f}%: sending...", end='', flush=True)
        
        # Retry logic
        max_retries = 2  # Initial attempt + 1 retry
        retry_count = 0
        success = False
        
        while retry_count <= max_retries and not success:
            try:
                start = time.time()
                res = requests.post(
                    f"{BASE_URL}/UserWatchStory/CreateOrUpdateLessonWatch",
                    headers=headers,
                    json=payload,
                    timeout=10
                )
                response_time = time.time() - start
                
                if res.status_code == 200:
                    timing.record_success(response_time)
                    print(f"\r        [⏳] {target_percent:.2f}%: ✓               ")
                    success = True
                    break
                    
                elif res.status_code == 429:
                    timing.record_error(429)
                    wait_time = timing.should_wait_after_429()
                    print(f"\r        [⏳] {target_percent:.2f}%: [429 RATE LIMIT]")
                    countdown(wait_time, prefix="            ")
                    retry_count += 1
                    
                elif res.status_code == 400:
                    timing.record_error(400)
                    err_data = res.json()
                    error_msg = err_data.get('error', '')
                    
                    if 'already' in error_msg.lower() or 'completed' in error_msg.lower():
                        print(f"\r        [⏳] {target_percent:.2f}%: ✓ (cached)      ")
                        success = True
                        break
                    else:
                        if retry_count < max_retries:
                            print(f"\r        [⏳] {target_percent:.2f}%: [400 ERROR - RETRY {retry_count+1}/{max_retries}]")
                            countdown(20, prefix="            ")
                            retry_count += 1
                        else:
                            print(f"\r        [⏳] {target_percent:.2f}%: [400 FAILED - SKIP]")
                            success = True  # Skip and continue
                            break
                        
                else:
                    timing.record_error(res.status_code)
                    if retry_count < max_retries:
                        print(f"\r        [⏳] {target_percent:.2f}%: [{res.status_code} ERROR - RETRY {retry_count+1}/{max_retries}]")
                        wait = int(timing.get_sleep_time(5))
                        countdown(wait, prefix="            ")
                        retry_count += 1
                    else:
                        print(f"\r        [⏳] {target_percent:.2f}%: [{res.status_code} FAILED - SKIP]")
                        success = True  # Skip and continue
                        break
                    
            except requests.exceptions.RequestException as e:
                if retry_count < max_retries:
                    print(f"\r        [⏳] {target_percent:.2f}%: [NETWORK ERROR - RETRY {retry_count+1}/{max_retries}]")
                    countdown(10, prefix="            ")
                    retry_count += 1
                else:
                    print(f"\r        [⏳] {target_percent:.2f}%: [NETWORK FAILED - SKIP]")
                    success = True  # Skip and continue
                    break
        
        current_percent = target_percent
        
        if target_percent < 100 and success:
            between_checkpoint = timing.get_sleep_time(1)
            time.sleep(between_checkpoint)
    
    print(f"    [✓] Lesson {lesson_id} done!")
    tracker.lesson_done()
    return True

def solve_quiz(quiz_id: int, name: str) -> bool:
    """Solve quiz with retry logic"""
    print(f"    [?] Quiz: {name}")
    
    if quiz_id in QUIZZES_DB:
        answers = QUIZZES_DB[quiz_id]
    else:
        try:
            start = time.time()
            res = requests.get(f"{BASE_URL}/Quiz/GetQuizById?id={quiz_id}", headers=headers, timeout=10)
            response_time = time.time() - start
            
            if res.status_code == 200:
                timing.record_success(response_time)
                data = res.json()
                questions = data.get('result', {}).get('questions', [])
                answers = [
                    {
                        "quizQuestionId": q['id'],
                        "answers": [{"answerId": q['questionAnswers'][0]['id'], "state": True}]
                    }
                    for q in questions
                ]
            else:
                timing.record_error(res.status_code)
                print(f"        [-] Failed to fetch quiz: {res.status_code}")
                return False
        except Exception as e:
            print(f"        [-] Error: {e}")
            return False
    
    payload = {"quizId": quiz_id, "quizQuestions": answers}
    
    max_retries = 2
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            start = time.time()
            res = requests.post(
                f"{BASE_URL}/Quiz/CheckQuizAndSaveResult",
                headers=headers,
                json=payload,
                timeout=10
            )
            response_time = time.time() - start
            
            if res.status_code == 200:
                timing.record_success(response_time)
                print(f"    [✓] Quiz {quiz_id} solved!")
                tracker.quiz_done()
                time.sleep(timing.get_sleep_time(2))
                return True
            else:
                timing.record_error(res.status_code)
                if retry_count < max_retries:
                    print(f"    [!] Quiz failed ({res.status_code}) - retry {retry_count+1}/{max_retries}")
                    countdown(15, prefix="        ")
                    retry_count += 1
                else:
                    print(f"    [-] Quiz failed permanently: {res.status_code}")
                    return False
                
        except Exception as e:
            if retry_count < max_retries:
                print(f"    [!] Quiz error - retry {retry_count+1}/{max_retries}")
                countdown(10, prefix="        ")
                retry_count += 1
            else:
                print(f"    [-] Quiz error: {e}")
                return False
    
    return False

def count_items(nodes: List[Dict]) -> tuple:
    lessons = 0
    quizzes = 0
    
    for node in nodes:
        if node.get('status') == 2:
            continue
            
        node_type = node.get('type')
        if node_type == 1:
            sub_l, sub_q = count_items(node.get('children', []))
            lessons += sub_l
            quizzes += sub_q
        elif node_type == 2:
            lessons += 1
        elif node_type == 3:
            quizzes += 1
    
    return lessons, quizzes

def process_tree_node(node: Dict):
    node_type = node.get('type')
    node_id = node.get('id')
    status = node.get('status')
    name = node.get('name', {}).get('uz', 'Unknown')
    
    if status == 2:
        if node_type == 2:
            tracker.lesson_done()
        elif node_type == 3:
            tracker.quiz_done()
        return
    
    if node_type == 1:
        print(f"[*] Module: {name}")
        for child in node.get('children', []):
            process_tree_node(child)
            
    elif node_type == 2:
        current_percent = node.get('percent', 0)
        watch_lesson_smart(node_id, name, current_percent)
        
    elif node_type == 3:
        solve_quiz(node_id, name)

def start_course(course_id: int):
    try:
        start = time.time()
        res = requests.post(
            f"{BASE_URL}/Progress/StartCourseProgress?courseId={course_id}",
            headers=headers,
            json={},
            timeout=10
        )
        response_time = time.time() - start
        
        if res.status_code == 200:
            timing.record_success(response_time)
            return True
        else:
            timing.record_error(res.status_code)
            return False
    except:
        return False

def get_course_tree(course_id: int) -> List[Dict]:
    try:
        start = time.time()

        res = requests.get(
            f"{BASE_URL}/Progress/GetPrivateCourseContentTree?courseId={course_id}",
            headers=headers,
            timeout=10
        )

        response_time = time.time() - start

        print(f"\n[DEBUG] Course {course_id}")
        print(f"[DEBUG] Status: {res.status_code}")
        print(f"[DEBUG] Response: {res.text[:500]}")

        if res.status_code == 200:
            timing.record_success(response_time)

            data = res.json()

            print(f"[DEBUG] Parsed result keys: {data.keys()}")

            return data.get('result', {}).get('children', [])

        else:
            timing.record_error(res.status_code)

    except Exception as e:
        print(f"[DEBUG] Exception: {e}")

    return []
def get_all_courses() -> List[Dict]:
    try:
        start = time.time()
        res = requests.get(f"{BASE_URL}/Course/GetAllCourses", headers=headers, timeout=10)
        response_time = time.time() - start
        
        if res.status_code == 200:
            timing.record_success(response_time)
            data = res.json()
            return data.get('result', {}).get('items', [])
        else:
            timing.record_error(res.status_code)
    except:
        pass
    return []

def main():
    print("\n[*] AI Study Automator - ADAPTIVE + RETRY cook45 edition")
    print(f"[*] Mode: {'FAST ⚡' if FAST_MODE else 'SAFE 🛡️'} + REAL-TIME ADAPTATION")
    print(f"[*] Checkpoints: {' → '.join([f'{x:.2f}%' for x in PROGRESS_CHECKPOINTS])}")
    print(f"[*] Retry policy: 1 retry with 20s wait, then skip on persistent errors\n")
    
    cert = check_certificate()
    if cert:
        cert_id = cert.get('id')
        full_name = cert.get('userFullName', 'Unknown')
        print(f"[+] Certificate exists: https://omp.aistudy.uz/certificate?id={cert_id}")
        send_telegram(cert_id, full_name)
        return
    
    print("[*] No certificate. Starting automation...\n")
    
    courses = get_all_courses()
    if not courses:
        print("[-] No courses found or token expired")
        return
    
    print(f"[*] Found {len(courses)} course(s)")
    
    print("[*] Analyzing course structure...")
    for course in courses:
        tree = get_course_tree(course['id'])
        lessons, quizzes = count_items(tree)
        tracker.update_totals(lessons, quizzes)
    
    print(f"[*] Total: {tracker.total_lessons} lessons + {tracker.total_quizzes} quizzes\n")
    
    for course in courses:
        course_id = course['id']
        course_name = course.get('courseName', {}).get('uz', f'Course {course_id}')
        
        print(f"{'='*60}")
        print(f"[*] {course_name}")
        print(f"{'='*60}")
        
        start_course(course_id)
        time.sleep(timing.get_sleep_time(2))
        
        tree = get_course_tree(course_id)
        if not tree:
            print("[-] Could not fetch course tree")
            continue
        
        for node in tree:
            process_tree_node(node)
        
        time.sleep(timing.get_sleep_time(3))
        cert = check_certificate()
        if cert:
            cert_id = cert.get('id')
            full_name = cert.get('userFullName', 'Unknown')
            
            elapsed = time.time() - tracker.start_time
            elapsed_str = str(timedelta(seconds=int(elapsed)))
            
            print(f"\n{'='*60}")
            print(f"[+] 🎉 CERTIFICATE ACQUIRED!")
            print(f"{'='*60}")
            print(f"User: {full_name}")
            print(f"Link: https://omp.aistudy.uz/certificate?id={cert_id}")
            print(f"Time: {elapsed_str}")
            print(f"Final stats: {timing.success_count} requests, {timing.error_count} errors")
            print(f"{'='*60}\n")
            
            send_telegram(cert_id, full_name)
            return
        
        time.sleep(timing.get_sleep_time(timing.between_courses))
    
    cert = check_certificate()
    if cert:
        cert_id = cert.get('id')
        full_name = cert.get('userFullName', 'Unknown')
        print(f"[+] Certificate: https://omp.aistudy.uz/certificate?id={cert_id}")
        send_telegram(cert_id, full_name)
    else:
        print("[-] No certificate generated")

if __name__ == "__main__":
    main()