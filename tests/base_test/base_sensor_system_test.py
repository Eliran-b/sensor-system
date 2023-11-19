import asyncio
import threading
import unittest
from common.common_config import CommonConfig
from common.external_queue_interface import ExternalQueueInterface
from services.monitor_service.monitor_service_utils.sensor_utils import SensorUtils


class BaseSensorSystemTest(unittest.IsolatedAsyncioTestCase):
    alert_service_queue: ExternalQueueInterface
    temperature_sensor_connector_queue: ExternalQueueInterface
    humidity_sensor_connector_queue: ExternalQueueInterface
    pressure_sensor_connector_queue: ExternalQueueInterface
    sensors_config_dict: dict
    clean_up_queues: list

    @classmethod
    def setUpClass(cls) -> None:
        cls.maxDiff = None
        cls.clean_up_queues = list()
        cls.sensors_config_dict = SensorUtils.get_config_dict()

        # set up queues
        cls.alert_service_queue = ExternalQueueInterface(queue_url=CommonConfig.ALERT_SERVICE_QUEUE_URL)
        cls.temperature_sensor_connector_queue = ExternalQueueInterface(queue_url=CommonConfig.TEMPERATURE_SENSOR_QUEUE_URL)
        cls.humidity_sensor_connector_queue = ExternalQueueInterface(queue_url=CommonConfig.HUMIDITY_SENSOR_QUEUE_URL)
        cls.pressure_sensor_connector_queue = ExternalQueueInterface(queue_url=CommonConfig.PRESSURE_SENSOR_QUEUE_URL)

    def tearDown(self) -> None:
        for q in self.clean_up_queues:
            while not q.empty():
                q.get(timeout=1)

    @staticmethod
    def stop_threads(threads: list[threading.Thread], exist_flag: threading.Event):
        # set the stop event to signal worker threads to exit
        exist_flag.set()

        # wait for worker threads to finish
        for thread in threads:
            thread.join()

        # clear the flag and the threads for the next run
        threads.clear()
        exist_flag.clear()

    async def run_task_until_complete(self, input_queues_list: list, threads: list, exit_flag: threading.Event):
        for queue_to_wait in set(input_queues_list):
            while not queue_to_wait.q.empty():
                await asyncio.sleep(1)

        self.stop_threads(threads, exit_flag)
