import functools
import threading
from common.utils.cached_instance import CachedInstance


class ThreadManager(metaclass=CachedInstance):
    def __init__(self, thread_target_partial: functools.partial, daemon: bool):
        self.thread_target_partial: functools.partial = thread_target_partial
        self.exit_flag: threading.Event = threading.Event()
        self.thread: threading.Thread = threading.Thread(target=self._run_thread_task, daemon=daemon)

    def start_thread(self):
        self.thread.start()

    def stop_thread(self):
        self.exit_flag.set()
        self.thread.join()

    def _run_thread_task(self):
        while not self.exit_flag.is_set():
            self.thread_target_partial()
