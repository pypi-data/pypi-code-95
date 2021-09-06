# -*- coding: utf-8 -*-

from abc import ABC


class ISwaggerService(ABC):
    """
    Interface to perform Swagger registrations.
    """

    def register_open_api_spec(self, base_route: str, swagger_route: str):
        """
        Perform required Swagger registration steps.
        """
