import asyncio
import unittest
from common.common_config import CommonConfig
from common.external_queue import ExternalQueue
from common.thread_event_notifier import ThreadEventNotifier
from common.utils.cached_instance import CachedInstance
from common.utils.singleton import Singleton
from services.monitor_service.monitor_service_utils.sensor_utils import SensorUtils


class BaseSensorSystemTest(unittest.IsolatedAsyncioTestCase):
    alert_service_queue: ExternalQueue
    temperature_sensor_connector_queue: ExternalQueue
    humidity_sensor_connector_queue: ExternalQueue
    pressure_sensor_connector_queue: ExternalQueue
    sensors_config_dict: dict
    clean_up_queues: list

    @classmethod
    def setUpClass(cls) -> None:
        cls.maxDiff = None
        cls.clean_up_queues = list()
        cls.input_queues_list = list()
        cls.sensors_config_dict = SensorUtils.get_config_dict()

    def setUp(self) -> None:
        # set up queues
        self.alert_service_queue = ExternalQueue(queue_url=CommonConfig.ALERT_SERVICE_QUEUE_URL)
        self.temperature_sensor_connector_queue = ExternalQueue(queue_url=CommonConfig.TEMPERATURE_SENSOR_QUEUE_URL)
        self.humidity_sensor_connector_queue = ExternalQueue(queue_url=CommonConfig.HUMIDITY_SENSOR_QUEUE_URL)
        self.pressure_sensor_connector_queue = ExternalQueue(queue_url=CommonConfig.PRESSURE_SENSOR_QUEUE_URL)

    def tearDown(self) -> None:
        for q in self.clean_up_queues:
            while not q.empty():
                q.get(timeout=1)

        # clear thread_managers for the next run.
        ThreadEventNotifier.thread_managers.clear()

        # make sure next run won't take the objects of the current flow
        Singleton._instances = {}
        CachedInstance._instances = {}

    @staticmethod
    def stop_threads():
        for thread in ThreadEventNotifier.thread_managers:
            thread.stop_thread()

    async def run_task_until_complete(self):
        for queue_to_wait in self.input_queues_list:
            while not queue_to_wait.q.empty():
                await asyncio.sleep(1)

        self.stop_threads()
