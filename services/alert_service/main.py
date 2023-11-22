from common.thread_event_notifier import ThreadEventNotifier
from services.alert_service.alert_observer import AlertObserver


def alert_service_main(daemon: bool = True):
    alert_observers = [AlertObserver()]
    ThreadEventNotifier().start_notifier_threads(message_target_list=alert_observers, daemon=daemon)


if __name__ == "__main__":
    alert_service_main()
