# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.services.IRegisterable
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    IRegisterable interface implementation

    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""
from abc import ABC


class IRegisterable(ABC):
    """
    Interface to perform on-demand registrations.
    """

    def register(self):
        """
        Perform required registration steps.
        """
        pass
