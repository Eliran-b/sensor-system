from abc import abstractmethod, ABC
from common.external_queue import ExternalQueue
from common.queue_objects.queue_message_object import QueueMessageObject


class ObserverInterface:
    external_queue: ExternalQueue

    @abstractmethod
    def run_flow(self, q_message_object: QueueMessageObject):
        pass
