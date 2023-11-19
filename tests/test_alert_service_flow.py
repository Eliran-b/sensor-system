import json
from common.enums.message_source_enum import MessageSourceEnum
from common.queue_objects.queue_message_object import QueueMessageObject
from services.alert_service.main import alert_service_main, alert_service_threads, alert_service_exit_flag
from tests.base_test.base_sensor_system_test import BaseSensorSystemTest


class TestAlertServiceFlow(BaseSensorSystemTest):

    async def test_alert_service_flow_success(self):
        test_message_data_list = [{"message": "PRESSURE: 0 is not in valid range [900, 1100]", "sensor_name": "PRESSURE"},
                                  {"message": "PRESSURE: 1200 is not in valid range [900, 1100]", "sensor_name": "PRESSURE"}
                                  ]

        queue_messages_list = list()
        for message_body in test_message_data_list:
            message_obj = QueueMessageObject.parse_obj({"queue_url": self.alert_service_queue.queue_url,
                                                        "message_body": message_body,
                                                        "message_attributes": {"message_source": MessageSourceEnum.PRESSURE_SENSOR.value}
                                                        })
            queue_messages_list.append(message_obj)
            self.alert_service_queue.q.put(message_obj.json())

        alert_service_main(daemon=False)
        await self.run_task_until_complete(input_queues_list=[self.alert_service_queue], threads=alert_service_threads, exit_flag=alert_service_exit_flag)

        # test the q is empty after message handle has finished
        self.assertEqual(self.alert_service_queue.q.qsize(), 0)

        # test dlq is empty
        self.assertEqual(self.alert_service_queue.dlq.qsize(), 0)

    async def test_alert_service_flow_failed(self):
        test_message_data_list = [{"message": "some message"},
                                  {}
                                  ]

        queue_messages_list = list()
        for message_body in test_message_data_list:
            message_obj = {"queue_url": self.alert_service_queue.queue_url,
                           "message_body": message_body,
                           "message_attributes": {"message_source": None}
                           }
            queue_messages_list.append(message_obj)
            self.alert_service_queue.q.put(json.dumps(message_obj))

        alert_service_main(daemon=False)
        await self.run_task_until_complete(input_queues_list=[self.alert_service_queue], threads=alert_service_threads, exit_flag=alert_service_exit_flag)

        # make sure that failed messages exist in the dlq
        self.assertEqual(self.alert_service_queue.dlq.qsize(), len(test_message_data_list))
        self.clean_up_queues.append(self.alert_service_queue.dlq)

        # test the q is empty after message handle has finished
        self.assertEqual(self.alert_service_queue.q.qsize(), 0)
