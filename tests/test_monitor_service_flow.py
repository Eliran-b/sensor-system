import json
from common.enums.message_source_enum import MessageSourceEnum
from common.queue_objects.queue_message_object import QueueMessageObject
from services.monitor_service.main import monitor_service_main, monitor_service_threads, monitor_service_exit_flag
from tests.base_test.base_sensor_system_test import BaseSensorSystemTest


class TestMonitorServiceFlow(BaseSensorSystemTest):

    async def test_monitor_service_flow_success(self):
        test_message_data_list = [{"message_body": {MessageSourceEnum.HUMIDITY_SENSOR.value: 0},
                                   "queue": self.humidity_sensor_connector_queue,
                                   "message_source": MessageSourceEnum.HUMIDITY_SENSOR.value,
                                   },
                                  {"message_body": {MessageSourceEnum.PRESSURE_SENSOR.value: 0},
                                   "queue": self.pressure_sensor_connector_queue,
                                   "message_source": MessageSourceEnum.PRESSURE_SENSOR.value,
                                   },
                                  {"message_body": {MessageSourceEnum.TEMPERATURE_SENSOR.value: 0},
                                   "queue": self.temperature_sensor_connector_queue,
                                   "message_source": MessageSourceEnum.TEMPERATURE_SENSOR.value,
                                   },
                                  ]

        messages_sent_to_monitor_service = list()

        for message_data in test_message_data_list:
            message_obj = QueueMessageObject.parse_obj({"queue_url": message_data["queue"].queue_url,
                                                        "message_body": message_data["message_body"],
                                                        "message_attributes": {"message_source": message_data["message_source"]}
                                                        })
            raw_message = message_obj.json()
            message_data["queue"].q.put(raw_message)
            messages_sent_to_monitor_service.append(raw_message)

        monitor_service_main(daemon=False)
        await self.run_task_until_complete(input_queues_list=[message_data["queue"] for message_data in test_message_data_list],
                                           threads=monitor_service_threads,
                                           exit_flag=monitor_service_exit_flag)

        alert_service_q_length = self._calculate_alert_service_q_data(queue_messages_list=messages_sent_to_monitor_service, test_message_data_list=test_message_data_list)
        self.assertEqual(alert_service_q_length, 1)

        for message_data in test_message_data_list:
            # test the q is empty after message handle has finished
            self.assertEqual(message_data["queue"].q.qsize(), 0)
            # test dlq is empty
            self.assertEqual(message_data["queue"].dlq.qsize(), 0)

        # test monitor service q is equal to the amount messages sent
        self.assertEqual(self.alert_service_queue.q.qsize(), alert_service_q_length)

        # test message content
        for _ in range(alert_service_q_length):
            message_in_q = self.alert_service_queue.q.get(timeout=1)
            expected_message = json.dumps({"queue_url": "https://ALERT_SERVICE_QUEUE_URL",
                                           "message_body": {"message": "PressureSensor: 0 is not in valid range [900, 1100]"},
                                           "message_attributes": {"message_source": "PressureSensor"}})
            self.assertEqual(message_in_q, expected_message)

    async def test_monitor_service_flow_failed(self):
        test_message_data_list = [{"message_body": {"humidity": 0},
                                   "queue": self.humidity_sensor_connector_queue,
                                   "message_source": "some sensor",
                                   },
                                  {"message_body": {},
                                   "queue": self.humidity_sensor_connector_queue,
                                   "message_source": MessageSourceEnum.HUMIDITY_SENSOR.value,
                                   },
                                  ]
        for message_data in test_message_data_list:
            message_obj_dict = {"queue_url": message_data["queue"].queue_url,
                                "message_body": message_data["message_body"],
                                "message_attributes": {"message_source": message_data["message_source"]}
                                }
            message_data["queue"].q.put(json.dumps(message_obj_dict))

        monitor_service_main(daemon=False)
        await self.run_task_until_complete(input_queues_list=[message_data["queue"] for message_data in test_message_data_list],
                                           threads=monitor_service_threads,
                                           exit_flag=monitor_service_exit_flag)

        # make sure that failed messages exist in the dlq
        self.assertEqual(self.humidity_sensor_connector_queue.dlq.qsize(), len(test_message_data_list))
        self.clean_up_queues.append(self.humidity_sensor_connector_queue.dlq)

        for message_data in test_message_data_list:
            # test the q is empty after message handle has finished
            self.assertEqual(message_data["queue"].q.qsize(), 0)

        # test monitor service q is equal to the amount messages sent
        self.assertEqual(self.alert_service_queue.q.qsize(), 0)

    def _calculate_alert_service_q_data(self, queue_messages_list: list, test_message_data_list: list) -> int:
        alert_service_q_length = 0
        for raw_message, message_data in zip(queue_messages_list, test_message_data_list):
            message_obj = QueueMessageObject.parse_raw(raw_message)
            message_source = message_data["message_source"]
            lower_valid_range, upper_valid_range = self.sensors_config_dict[message_source]["valid_range"]
            if not lower_valid_range <= message_obj.message_body[message_source] <= upper_valid_range:
                alert_service_q_length += 1
        return alert_service_q_length
