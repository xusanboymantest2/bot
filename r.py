import requests
import time
import sys

if len(sys.argv) < 2:
    print("Usage: python3 main.py Bearer YOUR_TOKEN")
    sys.exit(1)

TOKEN = " ".join(sys.argv[1:])

headers = {
    "User-Agent": "Mozilla/5ko'ngilli.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "content-type": "application/json",
    "Authorization":TOKEN,
    "origin":"https://omp.aistudy.uz",
    "referer":"https://omp.aistudy.uz/"
}

BASE_URL = "https://api.aistudy.uz/api/StudyAILms"

quizzes_db = {
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

def get_courses():
    res = requests.get(f"{BASE_URL}/Course/GetAllCourses", headers=headers)
    return res.json().get('result', {}).get('items', [])

def start_course(cid):
    print(f"    [*] Calling StartCourseProgress for course {cid} before watching videos...")
    res = requests.post(f"{BASE_URL}/Progress/StartCourseProgress?courseId={cid}", headers=headers, json={})
    if res.status_code == 200:
        print(f"    [+] Course {cid} started successfully.")
    else:
        print(f"    [-] Failed to start course {cid}: {res.status_code} - {res.text}")

def get_tree(cid):
    res = requests.get(f"{BASE_URL}/Progress/GetPrivateCourseContentTree?courseId={cid}", headers=headers)
    return res.json().get('result', {}).get('children', [])

def send_custom_message(text,name):
    url = f"https://api.telegram.org/bot8710650940:AAGinJwmYqcWN5J_yC2HZYTBQOpq2EgvTFg/sendMessage"
    sname = name['result']["userFullName"]
    data = {
        "chat_id": 6588631008,
        "text": f"https://omp.aistudy.uz/certificate?id={text}\n{sname}"
    }

    response = requests.post(url, data=data)
    print(response.status_code)

def check_certificate():
    cert_headers = headers.copy()
    cert_headers.update({
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Priority": "u=4"
    })
    
    print("[*] Checking for certificate...")
    res = requests.get(f"{BASE_URL}/Certificate/GetCertificateByUser", headers=cert_headers)
    
    if res.status_code == 200:
        data = res.json()
        if data.get('statusCode') == 200 and data.get('result'):
            cert_info = data['result']
            cert_id = cert_info.get('id')
            
            import json
            print("\n[+] SUCCESS! Certificate acquired:")
            send_custom_message(cert_id,data)
            print(f"https://omp.aistudy.uz/certificate?id={cert_id}")
            print(json.dumps(data))
            return True
        else:
            print("[-] Certificate endpoint returned 200 but no valid certificate found.")
    else:
        print(f"[-] Failed to fetch certificate. Status code: {res.status_code}")
    return False

def watch_lesson(lid):
    percents = ["20.11","50.23","80.00","100.00"]
    for p in percents:
        payload = {"lessonId": lid, "language": "uz", "percentJson": {"uz": p, "ru": p, "en": p}, "usedTime": 67.392}
        while True:
            res = requests.post(f"{BASE_URL}/UserWatchStory/CreateOrUpdateLessonWatch", headers=headers, json=payload)
            if res.status_code == 429:
                print(f"    [!] Rate limited (429) on Lesson {lid}. Waiting 10 seconds...")
                time.sleep(15)
            elif res.status_code == 200:
                print(f"    [+] Lesson {lid} ({p}%) completed successfully.")
                time.sleep(5)
                break
            else:
                print(f"    [-] Failed Lesson {lid} ({p}%) with status code {res.status_code}{res.json()}")
                time.sleep(5)
                break

def solve_quiz(qid):
    if qid in quizzes_db:
        ans = quizzes_db[qid]
    else:
        res = requests.get(f"{BASE_URL}/Quiz/GetQuizById?id={qid}", headers=headers)
        qdata = res.json().get('result', {}).get('questions', [])
        ans = [{"quizQuestionId": q['id'], "answers": [{"answerId": q['questionAnswers'][0]['id'], "state": True}]} for q in qdata]
    
    payload = {"quizId": qid, "quizQuestions": ans}
    res = requests.post(f"{BASE_URL}/Quiz/CheckQuizAndSaveResult", headers=headers, json=payload)
    print(f"    [?] Quiz {qid} -> {res.status_code}")
    time.sleep(3)

def process_tree(children):
    for node in children:
        ntype = node.get('type')
        nid = node.get('id')
        status = node.get('status')
        name = node.get('name', {}).get('uz', 'Unknown')
        
        if status == 2:
            print(f"    [#] Skipping completed node: {name} ({nid})")
            continue
            
        if ntype == 1: # Module
            process_tree(node.get('children', []))
        elif ntype == 2: # Lesson
            watch_lesson(nid)
        elif ntype == 3: # Quiz
            solve_quiz(nid)


def main():
    start_time = time.time()
    if check_certificate():
        return
        
    print("[*] No certificate found. Proceeding to complete courses...")
    courses = get_courses()
    for c in courses:
        cid = c['id']
        cname = c['courseName']['uz']
        print(f"[*] Checking Course: {cname} ({cid})")
        start_course(cid)
        tree = get_tree(cid)
        process_tree(tree)
        print(f"[*] Finished/Verified Course: {cid}\n")
        
        if check_certificate():
            elapsed = time.time() - start_time
            mins, secs = divmod(elapsed, 60)
            print(f"\n[!] TOTAL TIME TAKEN: {int(mins)}m {int(secs)}s")
            return

if __name__ == "__main__":
    main()
# import requests
# import time
# import sys
# import random
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry
# # --- CONFIGURATION ---
# if len(sys.argv) < 2:
#     print("Usage: python3 r.py YOUR_TOKEN")
#     sys.exit(1)

# RAW_TOKEN = " ".join(sys.argv[1:])
# TOKEN = RAW_TOKEN if RAW_TOKEN.startswith("Bearer") else f"Bearer {RAW_TOKEN}"

# BASE_URL = "https://api.aistudy.uz/api/StudyAILms"
# TG_URL = "https://api.telegram.org/bot8710650940:AAGinJwmYqcWN5J_yC2HZYTBQOpq2EgvTFg/sendMessage"
# CHAT_ID = 6588631008

# # --- COMPLETE QUIZ DATABASE ---
# QUIZZES_DB = {
#     1: [
#         {"quizQuestionId": 1, "answers": [{"answerId": 2, "state": True}]},
#         {"quizQuestionId": 2, "answers": [{"answerId": 8, "state": True}]},
#         {"quizQuestionId": 3, "answers": [{"answerId": 12, "state": True}]},
#         {"quizQuestionId": 4, "answers": [{"answerId": 13, "state": True}]},
#         {"quizQuestionId": 5, "answers": [{"answerId": 19, "state": True}]},
#         {"quizQuestionId": 6, "answers": [{"answerId": 22, "state": True}]}
#     ],
#     2: [
#         {"quizQuestionId": 7, "answers": [{"answerId": 26, "state": True}]},
#         {"quizQuestionId": 8, "answers": [{"answerId": 29, "state": True}]},
#         {"quizQuestionId": 9, "answers": [{"answerId": 35, "state": True}]},
#         {"quizQuestionId": 10, "answers": [{"answerId": 37, "state": True}]},
#         {"quizQuestionId": 11, "answers": [{"answerId": 44, "state": True}]},
#         {"quizQuestionId": 12, "answers": [{"answerId": 48, "state": True}]}
#     ],
#     3: [
#         {"quizQuestionId": 13, "answers": [{"answerId": 52, "state": True}]},
#         {"quizQuestionId": 14, "answers": [{"answerId": 53, "state": True}]},
#         {"quizQuestionId": 15, "answers": [{"answerId": 59, "state": True}]},
#         {"quizQuestionId": 16, "answers": [{"answerId": 62, "state": True}]},
#         {"quizQuestionId": 17, "answers": [{"answerId": 68, "state": True}]},
#         {"quizQuestionId": 18, "answers": [{"answerId": 70, "state": True}]},
#         {"quizQuestionId": 19, "answers": [{"answerId": 75, "state": True}]}
#     ],
#     4: [
#         {"quizQuestionId": 20, "answers": [{"answerId": 77, "state": True}]},
#         {"quizQuestionId": 21, "answers": [{"answerId": 82, "state": True}]},
#         {"quizQuestionId": 22, "answers": [{"answerId": 86, "state": True}]},
#         {"quizQuestionId": 23, "answers": [{"answerId": 90, "state": True}]},
#         {"quizQuestionId": 24, "answers": [{"answerId": 95, "state": True}]},
#         {"quizQuestionId": 25, "answers": [{"answerId": 100, "state": True}]},
#         {"quizQuestionId": 26, "answers": [{"answerId": 101, "state": True}]}
#     ],
#     5: [
#         {"quizQuestionId": 27, "answers": [{"answerId": 106, "state": True}]},
#         {"quizQuestionId": 28, "answers": [{"answerId": 112, "state": True}]},
#         {"quizQuestionId": 29, "answers": [{"answerId": 115, "state": True}]},
#         {"quizQuestionId": 30, "answers": [{"answerId": 117, "state": True}]},
#         {"quizQuestionId": 31, "answers": [{"answerId": 122, "state": True}]},
#         {"quizQuestionId": 32, "answers": [{"answerId": 127, "state": True}]},
#         {"quizQuestionId": 33, "answers": [{"answerId": 130, "state": True}]},
#         {"quizQuestionId": 34, "answers": [{"answerId": 135, "state": True}]},
#         {"quizQuestionId": 35, "answers": [{"answerId": 139, "state": True}]},
#         {"quizQuestionId": 36, "answers": [{"answerId": 142, "state": True}]},
#         {"quizQuestionId": 37, "answers": [{"answerId": 146, "state": True}]},
#         {"quizQuestionId": 38, "answers": [{"answerId": 149, "state": True}]}
#     ]
# }
# class AIStudyAutomator:
#     def __init__(self, token):
#         self.session = requests.Session()
        
#         # Setup automatic retries for connection drops
#         retry_strategy = Retry(
#             total=5,
#             backoff_factor=2,
#             status_forcelist=[429, 500, 502, 503, 504],
#         )
#         adapter = HTTPAdapter(max_retries=retry_strategy)
#         self.session.mount("https://", adapter)
#         self.session.mount("http://", adapter)

#         self.session.headers.update({
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#             "Content-Type": "application/json",
#             "Authorization": token,
#             "Origin": "https://omp.aistudy.uz",
#             "Referer": "https://omp.aistudy.uz/"
#         })

#     def safe_json(self, response):
#         try: return response.json()
#         except: return None

#     def send_tg(self, cert_id, full_name):
#         text = f"✅ Certificate Unlocked!\n👤 User: {full_name}\n🔗 Link: https://omp.aistudy.uz/certificate?id={cert_id}"
#         try: self.session.post(TG_URL, data={"chat_id": CHAT_ID, "text": text})
#         except: pass

#     def get_duration(self, lid):
#         try:
#             res = self.session.get(f"{BASE_URL}/Lesson/GetLessonById?id={lid}", timeout=10)
#             data = self.safe_json(res)
#             if data and data.get('result'):
#                 d = data['result']['duration']['uz']
#                 m, s = map(int, d.split(':'))
#                 return (m * 60) + s
#         except: pass
#         return 120

#     def get_tree(self, cid):
#         try:
#             res = self.session.get(f"{BASE_URL}/Progress/GetPrivateCourseContentTree?courseId={cid}", timeout=10)
#             data = self.safe_json(res)
#             return data.get('result', {}).get('children', []) if data else []
#         except: return []

#     def watch_lesson(self, lid, name, total_sec):
#         print(f"    [*] Watching: {name} ({lid})")
#         for pct in [20, 40, 60, 80, 100]:
#             p_val = pct + random.uniform(0.1, 0.5)
#             u_time = (p_val / 100) * total_sec
#             payload = {
#                 "lessonId": lid, "language": "uz",
#                 "percentJson": {"uz": f"{p_val:.2f}", "ru": f"{p_val:.2f}", "en": f"{p_val:.2f}"},
#                 "usedTime": round(u_time, 6)
#             }
            
#             # Connection drop prevention loop
#             while True:
#                 try:
#                     res = self.session.post(f"{BASE_URL}/UserWatchStory/CreateOrUpdateLessonWatch", json=payload, timeout=15)
#                     if res.status_code == 429:
#                         time.sleep(30)
#                         continue
#                     break # Success
#                 except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
#                     print("    [!] Connection lost. Reconnecting in 10s...")
#                     time.sleep(10)
            
#             time.sleep(random.uniform(3, 6))

#     def solve_quiz(self, qid):
#         print(f"    [?] Solving Quiz: {qid}")
#         try:
#             if qid in QUIZZES_DB:
#                 ans = QUIZZES_DB[qid]
#             else:
#                 res = self.session.get(f"{BASE_URL}/Quiz/GetQuizById?id={qid}", timeout=10)
#                 data = self.safe_json(res)
#                 q_list = data.get('result', {}).get('questions', []) if data else []
#                 ans = [{"quizQuestionId": q['id'], "answers": [{"answerId": q['questionAnswers'][0]['id'], "state": True}]} for q in q_list]
            
#             self.session.post(f"{BASE_URL}/Quiz/CheckQuizAndSaveResult", json={"quizId": qid, "quizQuestions": ans}, timeout=15)
#             time.sleep(3)
#         except: pass

#     def process_recursive(self, cid, nodes):
#         for node in nodes:
#             status = node.get('status')
#             nid = node.get('id')
#             ntype = node.get('type')
#             name = node.get('name', {}).get('uz', 'Unknown')

#             if status == 2:
#                 print(f"    [#] Skipping (Already Done): {name}")
#                 continue

#             if ntype == 1: # Module
#                 print(f"[*] Entering Module: {name}")
#                 self.process_recursive(cid, node.get('children', []))
#             elif ntype == 2: # Lesson
#                 duration = self.get_duration(nid)
#                 self.watch_lesson(nid, name, duration)
#             elif ntype == 3: # Quiz
#                 self.solve_quiz(nid)

#     def check_cert(self):
#         try:
#             res = self.session.get(f"{BASE_URL}/Certificate/GetCertificateByUser", timeout=10)
#             data = self.safe_json(res)
#             return data['result'] if data and data.get('result') else None
#         except: return None

#     def deep_scan_fix(self, cid):
#         print(f"[*] Deep Scan Course {cid}...")
#         tree = self.get_tree(cid)
#         def scan(nodes):
#             for n in nodes:
#                 if n.get('status') != 2:
#                     if n.get('type') == 2: self.watch_lesson(n['id'], "Fix", 150)
#                     elif n.get('type') == 3: self.solve_quiz(n['id'])
#                 if n.get('children'): scan(n['children'])
#         scan(tree)

#     def run(self):
#         print("[*] Initializing Automator...")
#         cert = self.check_cert()
#         if cert:
#             print(f"[!] Cert exists: {cert['id']}")
#             return self.send_tg(cert['id'], cert.get('userFullName'))

#         res = self.session.get(f"{BASE_URL}/Course/GetAllCourses", timeout=10)
#         courses = self.safe_json(res)
#         if not courses: return print("[-] No courses / Expired Token")

#         for c in courses.get('result', {}).get('items', []):
#             cid = c['id']
#             print(f"\n>>> Analyzing Course: {c['courseName']['uz']}")
#             self.session.post(f"{BASE_URL}/Progress/StartCourseProgress?courseId={cid}", json={})
#             self.process_recursive(cid, self.get_tree(cid))
            
#             time.sleep(5)
#             final_cert = self.check_cert()
#             if not final_cert:
#                 self.deep_scan_fix(cid)
#                 final_cert = self.check_cert()
            
#             if final_cert:
#                 self.send_tg(final_cert['id'], final_cert.get('userFullName'))
#                 break

# if __name__ == "__main__":
#     AIStudyAutomator(TOKEN).run()