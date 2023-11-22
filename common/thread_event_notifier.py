import concurrent.futures
import functools
from common.thread_manager import ThreadManager
from common.utils.observer_interface import ObserverInterface
from common.utils.singleton import Singleton


class ThreadEventNotifier(metaclass=Singleton):
    thread_managers: list[ThreadManager]

    def __new__(cls, *args, **kwargs):
        cls.thread_managers = list()
        return super(ThreadEventNotifier, cls).__new__(cls, *args, **kwargs)

    @staticmethod
    def _notifier_flow(observer_obj: ObserverInterface, wait_time_seconds: int = None,
                       max_messages_to_pull: int = None, max_workers: int = None):
        messages_to_process = observer_obj.external_queue.receive_messages(wait_time_seconds=wait_time_seconds,
                                                                           max_messages_to_pull=max_messages_to_pull)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers or 3) as executor:
            for message_object in messages_to_process:
                executor.submit(observer_obj.run_flow, message_object)

    @classmethod
    def start_notifier_threads(cls, message_target_list: list[ObserverInterface], daemon: bool, max_workers: int = None,
                               wait_time_seconds: int = None, max_messages_to_pull: int = None):
        for target_obj in message_target_list:
            flow_partial_call = functools.partial(cls._notifier_flow,
                                                  observer_obj=target_obj,
                                                  wait_time_seconds=wait_time_seconds,
                                                  max_messages_to_pull=max_messages_to_pull,
                                                  max_workers=max_workers)
            thread_manager = ThreadManager(thread_target_partial=flow_partial_call, daemon=daemon)
            cls.thread_managers.append(thread_manager)
            thread_manager.start_thread()
