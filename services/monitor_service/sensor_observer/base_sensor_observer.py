from common.common_config import CommonConfig
from common.enums.message_source_enum import MessageSourceEnum
from common.external_queue_interface import ExternalQueueInterface
from common.queue_objects.queue_message_object import QueueMessageObject
from common.utils.cached_instance import CachedInstanceMeta
from services.monitor_service.monitor_service_utils.monitor_service_exceptions import InvalidMessage
from services.monitor_service.monitor_service_utils.sensor_utils import SensorUtils


class BaseSensorObserver(metaclass=CachedInstanceMeta):
    external_queue: ExternalQueueInterface
    message_source: MessageSourceEnum
    utils: [SensorUtils]
    alert_service_queue: ExternalQueueInterface
    config_dict: dict

    def __new__(cls, *args, **kwargs):
        cls.init_class_attributes()
        return super(BaseSensorObserver, cls).__new__(cls)

    def __init__(self, queue_url: str, message_source: [MessageSourceEnum], utils_class: [SensorUtils] = SensorUtils):
        self.message_source = message_source
        self.external_queue = ExternalQueueInterface(queue_url=queue_url)
        self.utils = utils_class

    @staticmethod
    def init_class_attributes():
        # make sure that will initialize once
        if getattr(BaseSensorObserver, "alert_service_queue", None) is None:
            BaseSensorObserver.alert_service_queue = ExternalQueueInterface(queue_url=CommonConfig.ALERT_SERVICE_QUEUE_URL)
            BaseSensorObserver.config_dict = SensorUtils.get_config_dict()

    def _validate_config_rules(self, message_body: dict):
        sensor_value = message_body[self.message_source]
        lower_range, upper_range = self.config_dict[self.message_source]["valid_range"]
        if not lower_range <= sensor_value <= upper_range:
            warning_message = f"{self.message_source}: {sensor_value} is not in valid range {[lower_range, upper_range]}"
            print(warning_message)
            raise InvalidMessage(message=warning_message)

    def _send_alert(self, message_body: dict, message_source: MessageSourceEnum):
        self.alert_service_queue.send_message(queue_url=self.alert_service_queue.queue_url,
                                              message_source=message_source,
                                              message_body=message_body)

    def run_flow(self, q_message_object: QueueMessageObject):
        try:
            self._validate_config_rules(q_message_object.message_body)
            print("message is valid")
        except InvalidMessage as im:
            self._send_alert(message_body={"message": im.message}, message_source=q_message_object.message_attributes.message_source)
