import re
import pandas as pd
from typing import Union, Callable, Optional
from pandas import DataFrame, merge
from logging import Logger
from threading import Event
from collections import Counter

from .. import Fundamental, log
from ..tools._common import parse_list_of_str
from ..pricing.pricing import Stream


# re for ADC fields like started with "TR." case is ignored
ADC_PATTERN = re.compile(r"^tr\..+", re.I)

# re for ADC date fields ended witH ".date" case is ignored
ADC_DATE_PATTERN = re.compile(r"^.+\.date$", re.I)

# re for finding expressions inside ADC fields like
# "TR.F.TotRevPerShr(SDate=0,EDate=-2,Period=FY0,Frq=FY).date"
ADC_PARAM_IN_FIELDS = re.compile(r".*\(.+\).*")


def get_data(
    universe: Union[str, list],
    fields: Union[str, list],
    parameters: Union[str, dict, None] = None,
) -> DataFrame:
    """
    With this tool you can request data from ADC, realtime pricing data or
    combination of both;

    Parameters
    ----------
        universe: str | list ,
            instruments to request.
        fields: str | list .
            fields to request.
        parameters: str | dict,
            Single global parameter key=value or dictionary
            of global parameters to request.


    Returns
    -------
    pandas.DataFrame

     Examples
    --------
    >>> get_data(universe=['IBM.N', 'VOD.L'], fields=['BID', 'ASK'])
    >>> get_data(
    ...     universe=['GOOG.O', 'AAPL.O'],
    ...     fields=['TR.EV','TR.EVToSales'],
    ...     parameters = {'SDate': '0CY', 'Curn': 'CAD'}
    ...)
    >>> get_data(
    ...    universe=['IBM.N', 'VOD.L'],
    ...    fields=['BID', 'ASK', 'TR.Revenue'],
    ...    parameters = {'SCale':6, 'SDate':0, 'EDate':-3, 'FRQ':'FY'}
    ...)
    """
    _fundamental_data = Fundamental.get_data
    _pricing_stream = Stream(universe=universe, fields=fields)
    return _get_data(**locals())


def _get_data(
    _fundamental_data: Callable, _pricing_stream: Stream, **kwargs
) -> DataFrame:
    universe = kwargs.pop("universe")
    fields = parse_list_of_str(kwargs.pop("fields"))
    parameters = kwargs.pop("parameters")

    add_event = Event()
    adc_df, pricing_df = DataFrame(), DataFrame()
    logger = log.root_logger.getChild("get_data_call")

    adc_fields = [i for i in fields if re.match(ADC_PATTERN, i)]
    pricing_fields = [i for i in fields if i not in adc_fields]

    is_parameters_in_adc = any(
        i for i in adc_fields if re.match(ADC_PARAM_IN_FIELDS, i)
    )
    is_parameters_requested = parameters or is_parameters_in_adc

    _add_date_if_needed(
        adc_fields,
        [adc_fields, pricing_fields, is_parameters_requested],
        add_event=add_event,
    )

    if adc_fields:
        adc_df = _send_request(
            data_provider=_fundamental_data,
            params={
                "universe": universe,
                "fields": adc_fields,
                "parameters": parameters,
                "field_name": True,
            },
            logger=logger,
        )

    if pricing_fields:
        pricing_df = _get_snapshot(_pricing_stream, pricing_fields, logger)

    if pricing_df.empty:
        result = adc_df
    elif adc_df.empty:
        result = pricing_df
    elif is_parameters_requested:
        result = _custom_merge(adc_df, pricing_df, do_tear_down=add_event.is_set())
    else:
        result = merge(pricing_df, adc_df)

    return result


def _add_date_if_needed(fields: list, pre_conditions: list, add_event: Event) -> None:
    if all(pre_conditions):
        is_date_requested = any(i for i in fields if re.match(ADC_DATE_PATTERN, i))

        if not is_date_requested:
            first_field_parts = fields[0].split(".")
            first_field = f"{first_field_parts[0]}.{first_field_parts[1]}"

            fields.append(f"{first_field}.date")
            add_event.set()


def _send_request(data_provider: Callable, params: dict, logger: Logger) -> DataFrame:
    log_string = f"{params['fields']} for {params['universe']}"
    logger.info(f"Requesting {log_string} \n")

    response = data_provider(**params)

    logger.info(
        f"Request to {response.request_message.url.path} with {log_string}\n"
        f"status: {response.status}\n"
    )

    if not response.is_success:
        logger.error(f"{response.error_code}\n{response.error_message}\n")

    return response.data.df if response.data.df is not None else DataFrame()


def _rename_identical_columns(df: DataFrame, name: str, revert: bool = False) -> None:
    if revert:
        # fr"^{name}_\d+$" - searching columns like f"{name}_0", f"{name}_1"
        new_names = [name if re.match(fr"^{name}_\d+$", i) else i for i in df.columns]
    else:
        new_names = []
        count = 0
        for i in df.columns:
            if i == name:
                i = f"{i}_{count}"
                count += 1
            new_names.append(i)
    df.columns = new_names


def _custom_merge(df_1: DataFrame, df_2: DataFrame, do_tear_down: bool) -> DataFrame:
    date_column = "Date"
    instruments_column = "Instrument"

    counted_columns = Counter(df_1.columns)
    duplicated_columns = [i for i, n in counted_columns.items() if n > 1]

    if duplicated_columns:
        if date_column in duplicated_columns:
            date_column = f"{date_column}_0"

        for i in duplicated_columns:
            _rename_identical_columns(df_1, i)

    _convert_date_columns_to_datetime(df_1, pattern="Date")

    latest_rows_indexes = df_1.groupby(instruments_column)[date_column].idxmax()

    latest_info = df_1.loc[latest_rows_indexes]

    mediator = pd.merge(df_2, latest_info)
    result = pd.merge(mediator, df_1, how="right")

    if do_tear_down:
        result.pop(date_column)

    if duplicated_columns:
        for i in duplicated_columns:
            _rename_identical_columns(result, i, revert=True)

    return result


def _get_snapshot(stream: Stream, fields: list, logger: Logger) -> Optional[DataFrame]:
    logger.info(f"Requesting pricing info for {fields} via websocket\n")

    stream.open(with_updates=False)
    df = stream.get_snapshot(fields=fields)
    stream.close()

    return df


def _convert_date_columns_to_datetime(df: DataFrame, pattern: str) -> None:
    for i in df.columns:
        if pattern in i:
            df[i] = pd.to_datetime(df[i])
