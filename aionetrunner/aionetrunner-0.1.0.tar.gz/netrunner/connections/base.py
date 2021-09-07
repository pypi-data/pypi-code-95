from abc import ABC, abstractmethod


class Base(ABC):
    @abstractmethod
    async def open(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def connection_manager(self):
        pass

    @abstractmethod
    async def get_connection(self):
        pass
