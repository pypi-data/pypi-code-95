from abc import abstractmethod


class NehushtanMessageQueue:
    """
    This is a simplest model of Message Queue.
    Since 0.4.12
    """

    def __init__(self):
        pass

    @abstractmethod
    def push(self, item: str, queue_name: str):
        pass

    @abstractmethod
    def pop(self, queue_name: str):
        pass
