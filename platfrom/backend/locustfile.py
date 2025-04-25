import uuid
from datetime import datetime
from locust import HttpUser, task, between, events

INIT = {
    "group_id": None,
    "lesson_id": None,
    "homework_id": None,
    "teacher_token": None,
    "to_grade": set()
}

TEACHER_EMAIL = "teacher@example.com"
TEACHER_PWD = "teachpass"

class TeacherUser(HttpUser):
    wait_time = between(5, 10)

    def on_start(self):
        if INIT["teacher_token"]:
            self.headers = {"Authorization": f"Bearer {INIT['teacher_token']}"}
            return

        # Регистрация (может вернуть 400)
        self.client.post("/register", json={
            "name": "Teacher",
            "email": TEACHER_EMAIL,
            "password": TEACHER_PWD
        })

        # Логин
        login = self.client.post("/login", json={
            "email": TEACHER_EMAIL,
            "password": TEACHER_PWD
        })
        if login.status_code != 200:
            print(f"[ERROR] Login failed: {login.status_code}")
            return

        token = login.json().get("access_token")
        if not token:
            print("[ERROR] No access_token in login response")
            return
        INIT["teacher_token"] = token
        self.headers = {"Authorization": f"Bearer {token}"}

        # Группа
        group_name = f"Locust Group {uuid.uuid4().hex[:6]}"
        gr = self.client.post("/groups/", json={"name": group_name}, headers=self.headers)

        if gr.status_code != 200:
            print(f"[ERROR] /groups/ failed: {gr.status_code}, body={gr.text}")
            return
        try:
            INIT["group_id"] = gr.json()["id"]
        except Exception:
            print("[ERROR] group response is not JSON")
            return

        # Урок
        files = {
            "name": (None, "Load Lesson"),
            "description": (None, "For testing"),
            "text": (None, "Lesson content"),
            "date": (None, datetime.utcnow().isoformat()),
            "group_id": (None, str(INIT["group_id"]))
        }
        lsn = self.client.post("/lessons/", files=files, headers=self.headers)
        if lsn.status_code != 200:
            print(f"[ERROR] /lessons/ failed: {lsn.status_code}, body={lsn.text}")
            return
        INIT["lesson_id"] = lsn.json()["id"]

        # Домашка
        hw = self.client.post("/homeworks/", data={
            "lesson_id": INIT["lesson_id"],
            "description": "Solve task",
            "text": "Do it",
            "date": datetime.utcnow().isoformat()
        }, headers=self.headers)
        if hw.status_code != 200:
            print(f"[ERROR] /homeworks/ failed: {hw.status_code}, body={hw.text}")
            return
        INIT["homework_id"] = hw.json()["id"]

    @task
    def grade_submissions(self):
        if not INIT["homework_id"]:
            return
        r = self.client.get(f"/api/homework/{INIT['homework_id']}/submissions", headers=self.headers)
        if r.status_code != 200:
            return
        for sub in r.json():
            sid = sub["id"]
            if sid not in INIT["to_grade"]:
                g = self.client.post("/grade_homework", data={
                    "submission_id": sid,
                    "grade": 10
                }, headers=self.headers)
                if g.status_code == 200:
                    INIT["to_grade"].add(sid)


class StudentUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        if not INIT["group_id"]:
            return

        email = f"student_{uuid.uuid4().hex}@example.com"
        password = "studpass"

        self.client.post("/register", json={
            "name": "Student",
            "email": email,
            "password": password
        })

        login = self.client.post("/login", json={
            "email": email,
            "password": password
        })
        if login.status_code != 200:
            return

        data = login.json()
        self.user_id = data.get("id")
        token = data.get("access_token")
        if not self.user_id or not token:
            return

        self.headers = {"Authorization": f"Bearer {token}"}

        # Присоединяемся к группе
        self.client.post(f"/groups/join/{INIT['group_id']}", json={
            "user_id": self.user_id
        }, headers=self.headers)

    @task
    def submit_homework(self):
        if not INIT["homework_id"] or not hasattr(self, "user_id"):
            return
        self.client.post("/submit_homework", data={
            "homework_id": INIT["homework_id"],
            "user_id": self.user_id
        }, headers=self.headers)


@events.test_stop.add_listener
def cleanup(env, **kwargs):
    if not INIT["teacher_token"]:
        return

    headers = {"Authorization": f"Bearer {INIT['teacher_token']}"}
    client = env.runner.client

    if INIT["lesson_id"]:
        client.delete(f"/lessons/{INIT['lesson_id']}", headers=headers)
    if INIT["group_id"]:
        client.delete(f"/groups/{INIT['group_id']}", headers=headers)
