import concurrent.futures
import json
from typing import Callable
from common.external_queue_interface import ExternalQueueInterface


class ServiceUtils:

    @staticmethod
    def load_local_json_file(file_path: str) -> dict:
        with open(file_path, "r") as config_file:
            string_content = config_file.read()
        return json.loads(string_content)

    @staticmethod
    def run_service_flow(thread_flow_func: Callable, queue_url: str, wait_time_seconds: int = None, max_messages_to_pull: int = None, max_workers: int = None):
        monitor_service_q = ExternalQueueInterface(queue_url=queue_url)
        messages_to_process = monitor_service_q.receive_messages(wait_time_seconds=wait_time_seconds, max_messages_to_pull=max_messages_to_pull)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers or 3) as executor:
            for message_object in messages_to_process:
                executor.submit(thread_flow_func, message_object)
