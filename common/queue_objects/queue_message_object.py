from typing import Literal
from pydantic import BaseModel, validator, ValidationError
from common.common_config import CommonConfig
from common.queue_objects.message_attributes import MessageAttributes


class QueueMessageObject(BaseModel):
    queue_url: Literal[CommonConfig.ALERT_SERVICE_QUEUE_URL, CommonConfig.PRESSURE_SENSOR_QUEUE_URL,
                       CommonConfig.HUMIDITY_SENSOR_QUEUE_URL, CommonConfig.TEMPERATURE_SENSOR_QUEUE_URL,]
    message_body: dict
    message_attributes: MessageAttributes

    @validator('message_body')
    def validate_empty_value(cls, value):
        if not value:
            raise ValidationError("Value cannot be empty")
        return value
