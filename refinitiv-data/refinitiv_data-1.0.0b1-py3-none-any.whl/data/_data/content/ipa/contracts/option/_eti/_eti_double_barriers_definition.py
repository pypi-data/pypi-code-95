# coding: utf8

__all__ = ["EtiDoubleBarriersDefinition"]

from typing import Optional

from ._eti_barrier_definition import EtiBarrierDefinition
from ...instrument._instrument_definition import ObjectDefinition


class EtiDoubleBarriersDefinition(ObjectDefinition):
    """
    Parameters
    ----------
    barriers_definition : EtiBarrierDefinition, optional

    """

    def __init__(
        self,
        barriers_definition: Optional[EtiBarrierDefinition] = None,
    ) -> None:
        super().__init__()
        self.barriers_definition = barriers_definition

    @property
    def barriers_definition(self):
        """
        :return: list EtiBarrierDefinition
        """
        return self._get_list_parameter(EtiBarrierDefinition, "barriersDefinition")

    @barriers_definition.setter
    def barriers_definition(self, value):
        self._set_list_parameter(EtiBarrierDefinition, "barriersDefinition", value)
