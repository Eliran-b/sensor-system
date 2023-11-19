from common.common_config import CommonConfig
from common.enums.message_source_enum import MessageSourceEnum
from services.monitor_service.sensor_observer.base_sensor_observer import BaseSensorObserver


class TemperatureSensorObserver(BaseSensorObserver):
    def __init__(self):
        super().__init__(queue_url=CommonConfig.TEMPERATURE_SENSOR_QUEUE_URL, message_source=MessageSourceEnum.TEMPERATURE_SENSOR.value)
