import asyncio
import json
import queue
from pydantic import ValidationError
from common.enums.message_source_enum import MessageSourceEnum
from common.queue_objects.queue_message_object import QueueMessageObject
from common.utils.cached_instance import CachedInstance


class ExternalQueue(metaclass=CachedInstance):
    """This class simulate an external queue
        In real q there will be only the receive_messages API and the queue_url would be used to access the Q
    """
    q: queue.Queue
    queue_url: str

    def __init__(self, queue_url: str):
        self.queue_url = queue_url
        self.q = queue.Queue()
        self.dlq = queue.Queue()

    def _pull_message_from_q(self, max_messages_to_pull: int, messages_list: list) -> list:
        for _ in range(len(messages_list), max_messages_to_pull):
            item = self.q.get(timeout=1)
            try:
                q_message_object = QueueMessageObject.parse_raw(item)
            except (ValidationError, json.JSONDecodeError) as e:
                print(f"ERROR, could not parse q message. {e}")
                self.dlq.put(item=item)
                continue

            messages_list.append(q_message_object)

        return messages_list

    async def _async_get_messages_from_q(self, wait_time_seconds: int, max_messages_to_pull: int, messages_list: list) -> list:
        while len(messages_list) < max_messages_to_pull and wait_time_seconds:
            await asyncio.sleep(1)
            wait_time_seconds -= 1

            try:
                return self._pull_message_from_q(max_messages_to_pull=max_messages_to_pull, messages_list=messages_list)
            except queue.Empty:
                pass

        return messages_list

    def _get_messages_from_q(self, wait_time_seconds: int, max_messages_to_pull: int) -> list:
        """simulate Long Pulling from Q.
            the Q should wait for certain amount of messages or timeout to return response so our server could make less HTTP requests to the Q
            can be set to 0 by the caller if seeks less wait time in the processing

            if there is enough messages in the q pull them all
            if there is not enough message wait for more messages to come until max_messages_to_pull or wait_time_seconds has reached
        """
        messages_list = list()
        try:
            return self._pull_message_from_q(max_messages_to_pull=max_messages_to_pull, messages_list=messages_list)
        except queue.Empty:
            if not wait_time_seconds:
                return messages_list
            # set new event loop to run the task
            event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(event_loop)
            event_loop.run_until_complete(self._async_get_messages_from_q(wait_time_seconds=wait_time_seconds, max_messages_to_pull=max_messages_to_pull,
                                                                          messages_list=messages_list))
            event_loop.close()
            return messages_list

    def receive_messages(self, wait_time_seconds: int = None, max_messages_to_pull: int = None) -> list:
        wait_time_seconds = wait_time_seconds or 0
        max_messages_to_pull = max_messages_to_pull or 5
        return self._get_messages_from_q(wait_time_seconds=wait_time_seconds, max_messages_to_pull=max_messages_to_pull)

    @staticmethod
    def send_message(queue_url: str, message_source: MessageSourceEnum, message_body: dict):
        message_attributes = {"message_source": message_source}
        message = {"queue_url": queue_url, "message_body": message_body, "message_attributes": message_attributes}
        try:
            q_message_dict = QueueMessageObject.parse_obj(message).json()

            destination_q = ExternalQueue(queue_url=queue_url).q
            destination_q.put(item=q_message_dict)

            print(f"send message to q: {queue_url}, from source: {message_source}, body: {message_body}")
        except Exception as e:
            error_message = "Failed to send message to Q"
            print(f"{error_message}, {e}")

    def delete_message(self):
        """No need to implement cause python queue pop every message read"""
        pass
