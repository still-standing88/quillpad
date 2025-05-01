from typing import Optional
from dotenv import load_dotenv
from api import BlogApi, UserInfo
from agent import QuillpadAgent
import os
import random
import time
import threading
from queue import Queue, Empty

load_dotenv()

API_KEY = os.getenv("API_KEY") or ""
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") or "admin@example.com"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME") or "admin"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") or "admin123"
BASE_URL = os.getenv("BASE_URL") or "http://localhost:8000/api"
MODEL_NAME = os.getenv("MODEL_NAME") or "models/gemini-pro"
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPRATURE", "0.7"))

class SystemAgent:
    def __init__(self, min_active: int = 300, max_active: int = 600,
                 min_idle: int = 1800, max_idle: int = 10800):
        self.min_active = min_active
        self.max_active = max_active
        self.min_idle = min_idle
        self.max_idle = max_idle
        self.running = False
        self._main_thread: Optional[threading.Thread] = None
        self._processor_thread: Optional[threading.Thread] = None
        self._queue: Queue[str] = Queue()

        self.__blog = BlogApi(base_url=BASE_URL)
        self.__admin_user = UserInfo(username=ADMIN_USERNAME, email=ADMIN_EMAIL, password=ADMIN_PASSWORD, id=1)
        self.__agent = QuillpadAgent(self.__blog, API_KEY, MODEL_NAME, self.__admin_user, MODEL_TEMPERATURE, print_log=True)

    def start(self):
        self.running = True
        self._main_thread = threading.Thread(target=self._loop)
        self._processor_thread = threading.Thread(target=self._process_queue)
        self._main_thread.start()
        self._processor_thread.start()

    def stop(self):
        self.running = False
        if self._main_thread:
            self._main_thread.join()
        if self._processor_thread:
            self._processor_thread.join()

    def _loop(self):
        while self.running:
            active_duration = random.randint(self.min_active, self.max_active)
            print(f"[Agent] Starting active period ({active_duration}s)")
            burst_count = random.randint(9, 15)

            for _ in range(burst_count):
                self.enqueue_action()
                time.sleep(random.expovariate(1.0 / 5))  # short, random delay between bursts

            idle_time = random.randint(self.min_idle, self.max_idle)
            print(f"[Agent] Entering idle period ({idle_time}s)")
            time.sleep(idle_time)

    def enqueue_action(self):
        self._queue.put("What action to take?")

    def _process_queue(self):
        while self.running:
            try:
                msg = self._queue.get(timeout=1)
                self.__agent.send_msg(self.__agent.system_message(msg))
                self._queue.task_done()
            except Empty:
                continue

if __name__ == "__main__":
    agent = SystemAgent(3000, 4000, 180, 480)
    agent.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping agent...")
        agent.stop()
        del agent
        exit()
