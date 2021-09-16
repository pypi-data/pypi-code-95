# coding: utf8
from typing import List, Callable

import numpy as np
import pandas as pd
from numpy import iterable

from ._models._curve import Curve, ForwardCurve, ZcCurve
from .._content_provider import CurvesAndSurfacesRequestFactory, get_type_by_axis
from ..._content_provider import DataProvider, ResponseFactory
from ..._content_type import ContentType
from ....delivery.data.endpoint import EndpointData


# ---------------------------------------------------------------------------
#   Content data
# ---------------------------------------------------------------------------


def create_df(raw):
    data = raw.get("data", [])
    data = data or []
    data_frame = pd.DataFrame(data)

    if not data_frame.empty:
        data_frame = data_frame.convert_dtypes()

    return data_frame


def create_zc_curve_definitions_df(raw):
    data = raw.get("data", [])
    data = data or []
    curve_definitions = [d for d in data for d in d["curveDefinitions"]]
    data_frame = pd.DataFrame(curve_definitions)

    if not data_frame.empty:
        data_frame = data_frame.convert_dtypes()

    return data_frame


class BaseData(EndpointData):
    def __init__(self, raw, create_df=create_df):
        super().__init__(raw)
        self._create_df = create_df

    @property
    def df(self):
        if self._dataframe is None and self._raw:
            self._dataframe = self._create_df(self._raw)
        return self._dataframe


class OneCurveData(BaseData):
    def __init__(self, raw, create_curves):
        super().__init__(raw)
        self._create_curves = create_curves
        self._curve = None

    @property
    def curve(self) -> Curve:
        if self._curve is None:
            curve = self._create_curves(self._raw)
            self._curve = curve[0]
        return self._curve


class CurvesData(BaseData):
    def __init__(self, raw, create_curves):
        super().__init__(raw)
        self._create_curves = create_curves
        self._curves = None

    @property
    def curves(self) -> List[Curve]:
        if self._curves is None:
            self._curves = self._create_curves(self._raw)
        return self._curves


def make_create_forward_curves(x_axis: str, y_axis: str) -> Callable:
    """
    Parameters
    ----------
    x_axis: str
        Name of key in curve point data for build X axis
    y_axis: str
        Name of key in curve point data for build Y axis

    Returns
    -------
    Callable
    """

    def create_forward_curves(raw: dict) -> list:
        """
        Curve point in "curvePoints":
        {
            "discountFactor": 1.0,
            "endDate": "2021-02-01",
            "ratePercent": -2.330761285491212,
            "startDate": "2021-02-01",
            "tenor": "0D"
        }
        Parameters
        ----------
        raw

        Returns
        -------
        list of ForwardCurve
        """
        curves = []
        for data in raw.get("data"):
            for forward_curve in data.get("forwardCurves"):
                x, y = [], []
                for point in forward_curve.get("curvePoints"):
                    end_date = point.get(x_axis)
                    x.append(end_date)
                    discount_factor = point.get(y_axis)
                    y.append(discount_factor)

                x = np.array(x, dtype=get_type_by_axis(x_axis))
                y = np.array(y, dtype=get_type_by_axis(y_axis))
                curve = ForwardCurve(x, y, **forward_curve)
                curves.append(curve)

        return curves

    return create_forward_curves


def make_create_zc_curves(x_axis: str, y_axis: str) -> Callable:
    """
    Parameters
    ----------
    x_axis: str
        Name of key in curve point data for build X axis
    y_axis: str
        Name of key in curve point data for build Y axis

    Returns
    -------
    Callable
    """

    def create_zc_curves(raw: dict) -> list:
        """
        Curve point in "curvePoints":
        {
            "discountFactor": 1.0,
            "endDate": "2021-07-27",
            "ratePercent": -0.7359148312458879,
            "startDate": "2021-07-27",
            "tenor": "ON",
            "instruments": [
                {
                    "instrumentCode": "SARON.S"
                }
            ]
        }
        Parameters
        ----------
        raw

        Returns
        -------
        list of ZcCurve
        """
        curves = []
        for data in raw.get("data"):
            for index_tenor, zc_curve in data.get("curves").items():
                x, y = [], []
                for point in zc_curve.get("curvePoints"):
                    end_date = point.get(x_axis)
                    x.append(end_date)
                    discount_factor = point.get(y_axis)
                    y.append(discount_factor)

                x = np.array(x, dtype=get_type_by_axis(x_axis))
                y = np.array(y, dtype=get_type_by_axis(y_axis))
                curve = ZcCurve(x, y, index_tenor, **zc_curve)
                curves.append(curve)

        return curves

    return create_zc_curves


curves_maker_by_content_type = {
    ContentType.FORWARD_CURVE: make_create_forward_curves(
        x_axis="endDate", y_axis="discountFactor"
    ),
    ContentType.ZC_CURVES: make_create_zc_curves(
        x_axis="endDate", y_axis="discountFactor"
    ),
}


def get_curves_maker(content_type):
    curves_maker = curves_maker_by_content_type.get(content_type)

    if not curves_maker:
        raise ValueError(f"Cannot find curves_maker for content_type={content_type}")

    return curves_maker


# ---------------------------------------------------------------------------
#   Response factory
# ---------------------------------------------------------------------------


class CurvesResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        raw = data.get("content_data")

        universe = kwargs.get("universe")
        content_type = kwargs.get("__content_type__")

        inst = self.response_class(is_success=True, **data)

        if content_type is ContentType.ZC_CURVE_DEFINITIONS:
            data = BaseData(raw, create_df=create_zc_curve_definitions_df)

        else:
            curves_maker = get_curves_maker(content_type)
            if iterable(universe):
                data = CurvesData(raw, curves_maker)

            else:
                data = OneCurveData(raw, curves_maker)

        inst.data = data
        return inst


# ---------------------------------------------------------------------------
#   Data provider
# ---------------------------------------------------------------------------

curves_data_provider = DataProvider(
    request=CurvesAndSurfacesRequestFactory(),
    response=CurvesResponseFactory(),
)
