# coding: utf8

__all__ = ["UnderlyingContract"]

from typing import Optional

from . import UnderlyingPricingParameters
from ..instrument._instrument_definition import InstrumentDefinition
from ..._object_definition import ObjectDefinition


class UnderlyingContract(ObjectDefinition):
    """
    API endpoint for Financial Contract analytics,
    that returns calculations relevant to each contract type.

    Parameters
    ----------
    instrument_type : str, optional
        The type of instrument being defined.
    instrument_definition : object, optional
        Definition of the input contract
    pricing_parameters : UnderlyingPricingParameters, optional
        The pricing parameters to apply to this instrument. If pricing parameters are
        not provided at this level parameters defined globally at the request level are
        used. If no pricing parameters are provided globally default values apply.
    csa_tag : str, optional

    Examples
    --------
     >>> import refinitiv.data.content.ipa.financial_contracts as rdf
     >>> rdf.repo.UnderlyingContract(
     ...    instrument_type="Bond",
     ...    instrument_definition=rdf.bond.Definition(instrument_code="US191450264="),
     ...)
    """

    def __init__(
        self,
        instrument_type: Optional[str] = None,
        instrument_definition: Optional[object] = None,
        pricing_parameters: Optional[UnderlyingPricingParameters] = None,
        csa_tag: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.instrument_type = instrument_type
        self.instrument_definition = instrument_definition
        self.pricing_parameters = pricing_parameters
        self.csa_tag = csa_tag

    @property
    def instrument_definition(self):
        """
        Definition of the input contract
        :return: object InstrumentDefinition
        """
        return self._get_object_parameter(InstrumentDefinition, "instrumentDefinition")

    @instrument_definition.setter
    def instrument_definition(self, value):
        self._set_object_parameter(InstrumentDefinition, "instrumentDefinition", value)

    @property
    def pricing_parameters(self):
        """
        The pricing parameters to apply to this instrument. Optional.
        If pricing parameters are not provided at this level parameters defined globally at the request level are used. If no
        pricing parameters are provided globally default values apply.
        :return: object RepoUnderlyingPricingParameters
        """
        return self._get_object_parameter(
            UnderlyingPricingParameters, "pricingParameters"
        )

    @pricing_parameters.setter
    def pricing_parameters(self, value):
        self._set_object_parameter(
            UnderlyingPricingParameters, "pricingParameters", value
        )

    @property
    def csa_tag(self):
        """
        :return: str
        """
        return self._get_parameter("csaTag")

    @csa_tag.setter
    def csa_tag(self, value):
        self._set_parameter("csaTag", value)

    @property
    def instrument_type(self):
        """
        The type of instrument being defined.
        :return: str
        """
        return self._get_parameter("instrumentType")

    @instrument_type.setter
    def instrument_type(self, value):
        self._set_parameter("instrumentType", value)
