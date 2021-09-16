# coding: utf8

from enum import Enum, unique
from typing import Union

import numpy
from pandas import DataFrame

from .._content_provider import (
    DataProvider,
    ResponseFactory,
    ContentValidator,
    RequestFactory,
)
from .._content_type import ContentType
from ...tools._common import (
    urljoin,
    fields_arg_parser,
    make_enum_arg_parser,
)
from ...tools._datetime import hp_datetime_adapter


# ---------------------------------------------------------------------------
#   EventTypes
# ---------------------------------------------------------------------------


@unique
class EventTypes(Enum):
    """
    The list of market events (comma delimiter), supported event types are trade,
    quote and correction.
    Note: Currently support only single event type.
        If request with multiple event types,
        the backend will pick up the first event type to proceed.
    """

    TRADE = "trade"
    QUOTE = "quote"
    CORRECTION = "correction"


event_types_arg_parser = make_enum_arg_parser(EventTypes)


# ---------------------------------------------------------------------------
#   Intervals
# ---------------------------------------------------------------------------


class DayIntervalType(Enum):
    INTRA = 0
    INTER = 1


@unique
class Intervals(Enum):
    """
    The list of interval types of the boundary is described below.

    The supported values of intervals :

        Time:

        Backend will return complete N-minute summaries data. When the request start and/or end does not at the N minutes boundary, the response will be adjusted.

            ONE_MINUTE - return complete 1-minute
            FIVE_MINUTES - return complete 5-minutes
            TEN_MINUTES - return complete 10-minutes
            THIRTY_MINUTES - return complete 30-minutes
            SIXTY_MINUTES - return complete 60-minutes
            ONE_HOUR - return complete 1-hour

        Days:

            DAILY - This is end of day, daily data
            SEVEN_DAYS - Weekly boundary based on the exchange's week summarization definition
            WEEKLY - Weekly boundary based on the exchange's week summarization definition
            MONTHLY - Monthly boundary based on calendar month
            QUARTERLY - Quarterly boundary based on calendar quarter
            TWELVE_MONTHS - Yearly boundary based on calendar year
            YEARLY - Yearly boundary based on calendar year
    """

    ONE_MINUTE = "PT1M"
    FIVE_MINUTES = "PT5M"
    TEN_MINUTES = "PT10M"
    THIRTY_MINUTES = "PT30M"
    SIXTY_MINUTES = "PT60M"
    ONE_HOUR = "PT1H"
    DAILY = "P1D"
    SEVEN_DAYS = "P7D"
    WEEKLY = "P1W"
    MONTHLY = "P1M"
    QUARTERLY = "P3M"
    TWELVE_MONTHS = "P12M"
    YEARLY = "P1Y"


_ISO8601_INTERVALS = [k.value for k in Intervals]
"""['PT1M', 'PT5M', 'PT10M', 'PT30M', 'PT60M', 'PT1H']"""
_INTRADAY = _ISO8601_INTERVALS[:6]
"""['P1D', 'P7D', 'P1W', 'P1M', 'P3M', 'P12M', 'P1Y']"""
_INTERDAY = _ISO8601_INTERVALS[6:]

interval_arg_parser = make_enum_arg_parser(Intervals, can_be_lower=True)


def get_day_interval_type(
    interval: Union[str, Intervals, DayIntervalType]
) -> DayIntervalType:
    if isinstance(interval, DayIntervalType):
        return interval

    interval = interval_arg_parser.get_str(interval)

    if interval in _INTRADAY:
        day_interval_type = DayIntervalType.INTRA

    elif interval in _INTERDAY:
        day_interval_type = DayIntervalType.INTER

    else:
        raise TypeError(f"Incorrect day interval, interval={interval}.")

    return day_interval_type


content_type_by_day_interval_type = {
    DayIntervalType.INTER: ContentType.HISTORICAL_PRICING_INTERDAY_SUMMARIES,
    DayIntervalType.INTRA: ContentType.HISTORICAL_PRICING_INTRADAY_SUMMARIES,
}


def get_content_type_by_interval(
    interval: Union[str, Intervals, DayIntervalType]
) -> ContentType:
    day_interval_type = get_day_interval_type(interval)
    return content_type_by_day_interval_type.get(day_interval_type)


# ---------------------------------------------------------------------------
#   Adjustments
# ---------------------------------------------------------------------------


@unique
class Adjustments(Enum):
    """
    The list of adjustment types (comma delimiter) that tells the system whether
     to apply or not apply CORAX (Corporate Actions) events or
     exchange/manual corrections to historical time series data.

     The supported values of adjustments :

        UNADJUSTED - Not apply both exchange/manual corrections and CORAX
        EXCHANGE_CORRECTION - Apply exchange correction adjustment to historical pricing
        MANUAL_CORRECTION - Apply manual correction adjustment to historical pricing
                            i.e. annotations made by content analysts
        CCH - Apply Capital Change adjustment to historical Pricing due
              to Corporate Actions e.g. stock split
        CRE - Apply Currency Redenomination adjustment
              when there is redenomination of currency
        RPO - Apply Reuters Price Only adjustment
              to adjust historical price only not volume
        RTS - Apply Reuters TimeSeries adjustment
              to adjust both historical price and volume
        QUALIFIERS - Apply price or volume adjustment
              to historical pricing according to trade/quote qualifier
              summarization actions
    """

    UNADJUSTED = "unadjusted"
    EXCHANGE_CORRECTION = "exchangeCorrection"
    MANUAL_CORRECTION = "manualCorrection"
    CCH = "CCH"
    CRE = "CRE"
    RPO = "RPO"
    RTS = "RTS"
    QUALIFIERS = "qualifiers"


adjustments_arg_parser = make_enum_arg_parser(Adjustments)


# ---------------------------------------------------------------------------
#   MarketSession
# ---------------------------------------------------------------------------


@unique
class MarketSession(Enum):
    """
    The marketsession parameter represents a list of interested official durations
        in which trade and quote activities occur for a particular universe.

    The supported values of marketsession :

        PRE - specifies that data returned
              should include data during pre-market session
        NORMAL - specifies that data returned
                 should include data during normal market session
        POST - specifies that data returned
               should include data during post-market session
    """

    PRE = "pre"
    NORMAL = "normal"
    POST = "post"


market_sessions_arg_parser = make_enum_arg_parser(MarketSession)


# ---------------------------------------------------------------------------
#   ContentValidator
# ---------------------------------------------------------------------------


class HistoricalPricingContentValidator(ContentValidator):
    def validate_content_data(self, data):
        is_valid = True
        content_data = data.get("content_data")

        if isinstance(content_data, list) and len(content_data):
            content_data = content_data[0]
            status = content_data.get("status", {})

            if "Error" in status.get("code", ""):
                is_valid = False
                data["status"]["error"] = status
                data["error_code"] = status.get("code", -1)
                data["error_message"] = status.get("message")

        return is_valid


# ---------------------------------------------------------------------------
#   Response
# ---------------------------------------------------------------------------


def _convert_historical_json_to_pandas(json_historical_data):
    _headers = json_historical_data.get("headers")
    if _headers:
        _fields = [field["name"] for field in _headers]
        field_timestamp = None

        if "DATE_TIME" in _fields:
            field_timestamp = "DATE_TIME"
        elif "DATE" in _fields:
            field_timestamp = "DATE"

        if field_timestamp:
            _timestamp_index = _fields.index(field_timestamp)
            # remove timestamp from fields (timestamp is used as index for dataframe)
            _fields.pop(_timestamp_index)
        else:
            _fields = []
    else:
        _fields = []

    historical_dataframe = None
    _data = json_historical_data.get("data")

    if _data and _fields:
        # remove timestamp from array
        _timestamps = [l.pop(_timestamp_index) for l in _data]
        # build numpy array with all datapoints
        _numpy_array = numpy.array(_data)
        # build timestamp as index for dataframe
        _timestamp_array = numpy.array(_timestamps, dtype="datetime64")

        historical_dataframe = DataFrame(
            _numpy_array, columns=_fields, index=_timestamp_array
        )
        if not historical_dataframe.empty:
            historical_dataframe = (
                historical_dataframe.convert_dtypes()
            )  # convert_string=False)

        historical_dataframe.sort_index(inplace=True)

    return historical_dataframe


class HistoricalPricingResponseFactory(ResponseFactory):
    def create_success(self, *args, **kwargs):
        data = args[0]
        inst = self.response_class(is_success=True, **data)
        content_data = data.get("content_data")
        content_data = content_data[0]
        dataframe = _convert_historical_json_to_pandas(content_data)
        inst.data = self.data_class(content_data, dataframe)
        return inst


# ---------------------------------------------------------------------------
#   Request
# ---------------------------------------------------------------------------


class HistoricalPricingRequestFactory(RequestFactory):
    def get_url(self, *args, **kwargs):
        url = args[1]
        url = urljoin(url, "/{universe}")
        return url

    def get_path_parameters(self, *_, **kwargs):
        universe = kwargs.get("universe")
        return {"universe": universe}

    def get_field_timestamp(self, *args, **kwargs):
        return "DATE_TIME"

    def get_query_parameters(self, *args, **kwargs):
        query_parameters = []

        #
        # start
        #
        start = kwargs.get("start")
        if start:
            start = hp_datetime_adapter.get_str(start)
            query_parameters.append(("start", start))

        #
        # end
        #
        end = kwargs.get("end")
        if end:
            end = hp_datetime_adapter.get_str(end)
            query_parameters.append(("end", end))

        #
        # adjustments
        #
        adjustments = kwargs.get("adjustments")
        if adjustments:
            adjustments = adjustments_arg_parser.get_str(adjustments, delim=",")
            query_parameters.append(("adjustments", adjustments))

        #
        # market_sessions
        #
        market_sessions = kwargs.get("market_sessions")
        if market_sessions:
            market_sessions = market_sessions_arg_parser.get_str(
                market_sessions, delim=","
            )
            query_parameters.append(("sessions", market_sessions))

        #
        # count
        #
        count = kwargs.get("count") or 1
        if count < 1:
            raise AttributeError("Count minimum value is 1")

        if count > 1:
            query_parameters.append(("count", count))

        #
        # fields
        #
        fields = kwargs.get("fields")
        if fields:
            fields = fields_arg_parser.get_list(fields)
            field_timestamp = self.get_field_timestamp(*args, **kwargs)
            if field_timestamp not in fields:
                fields.append(field_timestamp)
            query_parameters.append(("fields", ",".join(fields)))

        return query_parameters


class HistoricalPricingEventsRequestFactory(HistoricalPricingRequestFactory):
    def get_query_parameters(self, *args, **kwargs):
        query_parameters = super().get_query_parameters(*args, **kwargs)

        #
        # event_types
        #
        event_types = kwargs.get("event_types")
        if event_types:
            event_types = event_types_arg_parser.get_str(event_types, delim=",")
            query_parameters.append(("eventTypes", event_types))

        return query_parameters


field_timestamp_by_day_interval_type = {
    DayIntervalType.INTER: "DATE",
    DayIntervalType.INTRA: "DATE_TIME",
}


class HistoricalPricingSummariesRequestFactory(HistoricalPricingRequestFactory):
    def get_field_timestamp(self, *args, **kwargs):
        day_interval_type = kwargs.get("day_interval_type")
        field_timestamp = field_timestamp_by_day_interval_type.get(day_interval_type)
        return field_timestamp

    def get_query_parameters(self, *args, **kwargs):
        query_parameters = super().get_query_parameters(*args, **kwargs)

        #
        # interval
        #
        interval = kwargs.get("interval")
        if interval:
            interval = interval_arg_parser.get_str(interval)
            query_parameters.append(("interval", interval))

        return query_parameters


# ---------------------------------------------------------------------------
#   Providers
# ---------------------------------------------------------------------------

hp_events_data_provider = DataProvider(
    request=HistoricalPricingEventsRequestFactory(),
    response=HistoricalPricingResponseFactory(),
    validator=HistoricalPricingContentValidator(),
)

hp_summaries_data_provider = DataProvider(
    request=HistoricalPricingSummariesRequestFactory(),
    response=HistoricalPricingResponseFactory(),
    validator=HistoricalPricingContentValidator(),
)
