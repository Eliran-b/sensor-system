from enum import Enum


class MessageSourceEnum(Enum):
    TEMPERATURE_SENSOR = "TemperatureSensor"
    HUMIDITY_SENSOR = "HumiditySensor"
    PRESSURE_SENSOR = "PressureSensor"
