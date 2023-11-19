import threading
from common.utils.service_utils import ServiceUtils
from services.monitor_service.sensor_observer.base_sensor_observer import BaseSensorObserver
from services.monitor_service.sensor_observer.humidity_sensor_observer import HumiditySensorObserver
from services.monitor_service.sensor_observer.pressure_sensor_observer import PressureSensorObserver
from services.monitor_service.sensor_observer.temperature_sensor_observer import TemperatureSensorObserver

monitor_service_threads = list()
monitor_service_exit_flag = threading.Event()


def run_observer_monitor(sensor_observer: BaseSensorObserver):
    while not monitor_service_exit_flag.is_set():
        ServiceUtils.run_service_flow(thread_flow_func=sensor_observer.run_flow, queue_url=sensor_observer.external_queue.queue_url)


def monitor_service_main(daemon: bool = True):
    sensor_observers = [HumiditySensorObserver(), PressureSensorObserver(), TemperatureSensorObserver()]
    for sensor_observer in sensor_observers:
        thread = threading.Thread(target=run_observer_monitor, args=(sensor_observer,), daemon=daemon)
        monitor_service_threads.append(thread)
        thread.start()


if __name__ == "__main__":
    monitor_service_main()

