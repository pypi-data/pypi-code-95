# coding: utf8


from .._object_definition import ObjectDefinition

from ._enums import EtiInputVolatilityType
from ._enums import VolatilityModel
from ._enums import PriceSide
from ._enums import TimeStamp
from ._enums import MoneynessType
from ._enums import Axis
from ._models import MoneynessWeight
from ._models import SurfaceFilters


class EtiSurfaceParameters(ObjectDefinition):
    def __init__(
        self,
        filters=None,
        input_volatility_type=None,
        moneyness_type=None,
        price_side=None,
        time_stamp=None,
        volatility_model=None,
        weights=None,
        x_axis=None,
        y_axis=None,
        calculation_date=None,
        svi_alpha_extrapolation=None,
    ):
        super().__init__()
        self.filters = filters
        self.input_volatility_type = input_volatility_type
        self.moneyness_type = moneyness_type
        self.price_side = price_side
        self.time_stamp = time_stamp
        self.volatility_model = volatility_model
        self.weights = weights
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.calculation_date = calculation_date
        self.svi_alpha_extrapolation = svi_alpha_extrapolation

    @property
    def filters(self):
        """
        The details of the filtering
        :return: object SurfaceFilters
        """
        return self._get_object_parameter(SurfaceFilters, "filters")

    @filters.setter
    def filters(self, value):
        self._set_object_parameter(SurfaceFilters, "filters", value)

    @property
    def input_volatility_type(self):
        """
        Specifies the type of volatility used as an input of the model (calculated Implied Volatility, Settlement)

         - Settle: [DEPRECATED] The service uses the settlement volatility to build the volatility surface

         - Quoted: The service uses the quoted volatility to build the volatility surface

         - Implied: The service internally calculates implied volatilities for the option universe before building the surface

        Default value is "Implied".
        :return: enum EtiInputVolatilityType
        """
        return self._get_enum_parameter(EtiInputVolatilityType, "inputVolatilityType")

    @input_volatility_type.setter
    def input_volatility_type(self, value):
        self._set_enum_parameter(EtiInputVolatilityType, "inputVolatilityType", value)

    @property
    def moneyness_type(self):
        """
        The enumerate that specifies the moneyness type to use for calibration.
        - Spot
        - Fwd
        - Sigma
        Optional. Default value is "Spot".
        :return: enum MoneynessType
        """
        return self._get_enum_parameter(MoneynessType, "moneynessType")

    @moneyness_type.setter
    def moneyness_type(self, value):
        self._set_enum_parameter(MoneynessType, "moneynessType", value)

    @property
    def price_side(self):
        """
        Specifies whether bid, ask or mid is used to build the surface.
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def time_stamp(self):
        """
        Define how the timestamp is selected:
        - Open: the opening value of the valuationDate or if not available the close of the previous day is used.
        - Default: the latest snapshot is used when valuationDate is today, the close price when valuationDate is in the past.
        :return: enum TimeStamp
        """
        return self._get_enum_parameter(TimeStamp, "timeStamp")

    @time_stamp.setter
    def time_stamp(self, value):
        self._set_enum_parameter(TimeStamp, "timeStamp", value)

    @property
    def volatility_model(self):
        """
        The quantitative model used to generate the volatility surface. This may depend on the asset class.
        :return: enum VolatilityModel
        """
        return self._get_enum_parameter(VolatilityModel, "volatilityModel")

    @volatility_model.setter
    def volatility_model(self, value):
        self._set_enum_parameter(VolatilityModel, "volatilityModel", value)

    @property
    def weights(self):
        """
        Specifies the list of calibration weight.
        :return: list MoneynessWeight
        """
        return self._get_list_parameter(MoneynessWeight, "weights")

    @weights.setter
    def weights(self, value):
        self._set_list_parameter(MoneynessWeight, "weights", value)

    @property
    def x_axis(self):
        """
        Specifies the unit for the x axis (e.g. Date, Tenor)
        :return: enum Axis
        """
        return self._get_enum_parameter(Axis, "xAxis")

    @x_axis.setter
    def x_axis(self, value):
        self._set_enum_parameter(Axis, "xAxis", value)

    @property
    def y_axis(self):
        """
        Specifies the unit for the y axis (e.g. Strike, Delta). This may depend on the asset class.
        For Fx Volatility Surface, we support both Delta and Strike.
        :return: enum Axis
        """
        return self._get_enum_parameter(Axis, "yAxis")

    @y_axis.setter
    def y_axis(self, value):
        self._set_enum_parameter(Axis, "yAxis", value)

    @property
    def calculation_date(self):
        """
        The date the volatility surface is generated.
        :return: str
        """
        return self._get_parameter("calculationDate")

    @calculation_date.setter
    def calculation_date(self, value):
        self._set_parameter("calculationDate", value)

    @property
    def svi_alpha_extrapolation(self):
        """
        Svi Alpha Extrapolation for building the surface
        Default value : TRUE
        :return: bool
        """
        return self._get_parameter("sviAlphaExtrapolation")

    @svi_alpha_extrapolation.setter
    def svi_alpha_extrapolation(self, value):
        self._set_parameter("sviAlphaExtrapolation", value)
