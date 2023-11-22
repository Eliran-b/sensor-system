from common.thread_event_notifier import ThreadEventNotifier
from services.monitor_service.sensor_observer.humidity_sensor_observer import HumiditySensorObserver
from services.monitor_service.sensor_observer.pressure_sensor_observer import PressureSensorObserver
from services.monitor_service.sensor_observer.temperature_sensor_observer import TemperatureSensorObserver


def monitor_service_main(daemon: bool = True):
    sensor_observers = [HumiditySensorObserver(), PressureSensorObserver(), TemperatureSensorObserver()]
    ThreadEventNotifier().start_notifier_threads(message_target_list=sensor_observers, daemon=daemon)


if __name__ == "__main__":
    monitor_service_main()

