import json
import os
from pathlib import Path
from common.common_config import CommonConfig
from common.external_queue import ExternalQueue
from common.queue_objects.queue_message_object import QueueMessageObject
from common.utils.cached_instance import CachedInstance
from common.utils.observer_interface import ObserverInterface
from common.utils.service_utils import ServiceUtils


class AlertObserver(ObserverInterface, metaclass=CachedInstance):

    def __init__(self):
        self.config_dict = self._load_config_dict()
        self.external_queue = ExternalQueue(queue_url=CommonConfig.ALERT_SERVICE_QUEUE_URL)

    @staticmethod
    def _load_config_dict() -> dict:
        current_path = Path(__file__).parent
        config_file_path = os.path.join(current_path, "config.json")
        return ServiceUtils.load_local_json_file(file_path=config_file_path)

    @staticmethod
    def _push_sns_notification(sns_topic: str, message_to_publish: str):
        print(f"sending sns message: {message_to_publish} to: {sns_topic}")

    def run_flow(self, q_message_object: QueueMessageObject):
        print(f"Got message: {q_message_object.dict()}")
        try:
            message_source = q_message_object.message_attributes.message_source
            sns_topic = self.config_dict["SNS_TOPIC_MAPPER"][message_source]
            message_to_publish = json.dumps(q_message_object.message_body["message"], indent=4)
            self._push_sns_notification(sns_topic, message_to_publish)
        except KeyError as e:
            print(f"KeyError {e} missing in message or does not exist in mapper")
