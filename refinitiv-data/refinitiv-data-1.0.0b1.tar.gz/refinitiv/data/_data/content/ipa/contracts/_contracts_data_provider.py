import numpy
from pandas import DataFrame

from ._outputs import Outputs
from ..._content_provider import (
    RequestFactory,
    DataProvider,
    ResponseFactory,
)
from ....delivery.data.endpoint import RequestMethod, EndpointData
from ....tools._common import (
    ArgsParser,
    iterable,
    make_enum_arg_parser,
    fields_arg_parser,
)


class Data(EndpointData):
    """
    This class is designed for storing and managing the response instrument data
    """

    def __init__(self, raw):
        super().__init__(raw)
        self._analytics_headers = None
        self._analytics_data = None
        self._analytics_market_data = None
        self._analytics_statuses = None
        if raw:
            #   get headers
            self._analytics_headers = raw.get("headers")
            #   get data
            self._analytics_data = raw.get("data")
            #   get marketData
            self._analytics_market_data = raw.get("marketData")
            #   get statuses
            self._analytics_statuses = raw.get("statuses")

    @property
    def analytics_headers(self):
        return self._analytics_headers

    @property
    def analytics_data(self):
        return self._analytics_data

    @property
    def analytics_market_data(self):
        return self._analytics_market_data

    @property
    def analytics_statuses(self):
        return self._analytics_statuses

    @property
    def df(self):
        """
        Convert "data" from raw response bond to dataframe format
        """
        data_dataframe = None
        if self.analytics_data:
            headers = [header["name"] for header in self.analytics_headers]
            numpy_array = numpy.array(self.analytics_data, dtype=object)
            data_dataframe = DataFrame(numpy_array, columns=headers)
            if not data_dataframe.empty:
                data_dataframe = data_dataframe.convert_dtypes()
        else:
            data_dataframe = DataFrame([], columns=[])
        return data_dataframe

    @property
    def marketdata_df(self):
        """
        Convert "marketData" from raw response bond to dataframe format
        """
        return None


def get_data(definition, pricing_parameters=None):
    if hasattr(definition, "_kwargs"):
        attr = getattr(definition, "_kwargs")
        definition = attr.get("definition")

    data = {
        "instrumentType": definition.get_instrument_type(),
        "instrumentDefinition": definition.get_json(),
    }

    if pricing_parameters:
        data["pricingParameters"] = pricing_parameters.get_json()

    return data


class ContractsRequestFactory(RequestFactory):
    def get_request_method(self, *_, **kwargs):
        return kwargs.get("method", RequestMethod.POST)

    def get_body_parameters(self, *_, **kwargs):
        input_universe = kwargs.get("universe")
        input_universe = input_universe or kwargs.get("definition") or []
        pricing_parameters = kwargs.get("pricing_parameters")
        fields = kwargs.get("fields") or []
        outputs = kwargs.get("outputs")

        if not isinstance(input_universe, list):
            input_universe = [input_universe]

        universe = []
        # convert universe's objects into json
        for i, item in enumerate(input_universe):
            # item can be a tuple (instrument, pricing_parameters)
            if iterable(item):
                data = get_data(*item)

            else:
                data = get_data(item)

            universe.append(data)

        body_parameters = {"universe": universe}

        if fields:
            fields = fields_arg_parser.get_list(fields)
            body_parameters["fields"] = fields

        if outputs:
            outputs = outputs_contracts_arg_parser.get_list(outputs)
            body_parameters["outputs"] = outputs

        if pricing_parameters:
            body_parameters["pricingParameters"] = pricing_parameters.get_json()

        return body_parameters


def process_universe_item(item, definition_class):
    # item can be empty string ""
    if item and isinstance(item, str):
        item = definition_class(item)

    elif isinstance(item, definition_class):
        return item

    else:
        raise ValueError(
            f"Invalid type of universe, expected str: {type(item)} is given"
        )

    return item


def process_universe(universe, definition_class, pricing_parameters_class=None):
    if iterable(universe):
        for i, item in enumerate(universe):

            if iterable(item):
                item, pricing_parameters = item

                if pricing_parameters_class and not isinstance(
                    pricing_parameters, pricing_parameters_class
                ):
                    raise ValueError(
                        f"Invalid type of pricing parameters, "
                        f"expected {pricing_parameters_class}: "
                        f"{type(pricing_parameters)} is given"
                    )

                item = process_universe_item(item, definition_class)
                item = (item, pricing_parameters)

            else:
                item = process_universe_item(item, definition_class)

            universe[i] = item

    else:
        universe = process_universe_item(universe, definition_class)

    return universe


universe_contracts_arg_parser = ArgsParser(process_universe)
outputs_contracts_arg_parser = make_enum_arg_parser(Outputs)

contracts_data_provider = DataProvider(
    request=ContractsRequestFactory(), response=ResponseFactory(data_class=Data)
)
