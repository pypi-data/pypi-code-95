# Copyright (c) 2020. All rights reserved.

import logging
from typing import TypeVar, Type, Dict


class AppContext:
    __instance_map__ = dict()

    T = TypeVar('T')

    @staticmethod
    def get_service(service_class: Type[T], config: Dict, logger: logging.Logger) -> T:
        new_instance = service_class(config, logger)
        service_instance = AppContext.__instance_map__.setdefault(service_class, new_instance)
        if service_instance == new_instance:
            if hasattr(service_instance, 'start'):
                service_instance.start()
        return service_instance

    @staticmethod
    def stop():
        for service_instance in AppContext.__instance_map__.values():
            if hasattr(service_instance, 'stop'):
                service_instance.stop()
