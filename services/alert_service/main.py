import json
import os.path
import threading
from common.common_config import CommonConfig
from common.utils.service_utils import ServiceUtils
from common.queue_objects.queue_message_object import QueueMessageObject
from pathlib import Path

current_path = Path(__file__).parent
config_file_path = os.path.join(current_path, "config.json")
config_dict = ServiceUtils.load_local_json_file(file_path=config_file_path)
alert_service_threads = list()
alert_service_exit_flag = threading.Event()


def push_sns_notification(sns_topic: str, message_to_publish: str):
    print(f"sending sns message: {message_to_publish} to: {sns_topic}")


def run_alert_service_thread_flow(queue_message_object: QueueMessageObject):
    print(f"Got message: {queue_message_object.dict()}")
    try:
        message_source = queue_message_object.message_attributes.message_source
        sns_topic = config_dict["SNS_TOPIC_MAPPER"][message_source]
        message_to_publish = json.dumps(queue_message_object.message_body["message"], indent=4)
        push_sns_notification(sns_topic, message_to_publish)
    except KeyError as e:
        print(f"KeyError {e} missing in message or does not exist in mapper")


def run_alert_observer():
    while not alert_service_exit_flag.is_set():
        ServiceUtils.run_service_flow(thread_flow_func=run_alert_service_thread_flow, queue_url=CommonConfig.ALERT_SERVICE_QUEUE_URL)


def alert_service_main(daemon: bool = True):
    alert_service_threads.append(threading.Thread(target=run_alert_observer, daemon=daemon))
    alert_service_threads[0].start()


if __name__ == "__main__":
    alert_service_main()
