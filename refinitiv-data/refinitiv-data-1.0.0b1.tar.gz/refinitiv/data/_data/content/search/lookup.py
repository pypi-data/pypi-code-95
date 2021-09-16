# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import asyncio

from collections import OrderedDict
from typing import Callable

from pandas import DataFrame

###############################################################
#
#   REFINITIV IMPORTS
#

from ...delivery.data import Endpoint
from ...tools._common import urljoin
from .SearchViews import SearchViews
from refinitiv.data._data.core.session import Session
from ...tools._repr_definition import create_str_definition


###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASSES
#


class Lookup(object):
    """this class is designed to handle the request and response for lookup in search api"""

    #   endpoint information
    #   endpoint request body keyword parameter names (require field)
    #       view
    _EndPointViewParameterName = "View"
    #       terms
    _EndPointTermsParameterName = "Terms"
    #       scope
    _EndPointScopeParameterName = "Scope"
    #       select
    _EndPointSelectParameterName = "Select"

    #   optional
    #       filter
    _EndPointFilterParameterName = "Filter"
    #       boost
    _EndPointBoostParameterName = "Boost"

    class LookupData(Endpoint.EndpointData):
        """this class is designed for storing and managing the response lookup data

        Response example
        I.
        {
            "Matches": {
                    "A": {
                        "DocumentTitle": "Agilent Technologies Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        },
                    "B": {
                        "DocumentTitle": "Barnes Group Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        },
                    "C": {
                        "DocumentTitle": "Citigroup Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        }
                }
        }

        II.
        {
            "Matches": {
                        "B": {
                            "DocumentTitle": "This one worked fine",
                            "ExchangeCountry": "USA"
                            }
            },
            "FailedSubRequests": {
                        "A": "(timed out)"
            }
        }

        """

        #   reponse keyword name
        _ResponseMatchesName = "Matches"
        _ReponseFailedSubRequestsName = "FailedSubRequests"
        _ReponseWarningsName = "Warnings"

        def __init__(self, raw):
            Endpoint.EndpointData.__init__(self, raw)

            #   convert raw data to dataframe and index
            self._dataframe = self._convertLookupResponseToDataframe(raw)

        @staticmethod
        def _convertLookupResponseToDataframe(raw):
            """convert a lookup response to the dataframe format"""
            assert Lookup.LookupData._ResponseMatchesName in raw
            matches = raw[Lookup.LookupData._ResponseMatchesName]

            ###########################################################
            #       matches
            #   loop over all matches and construct the dataframe format
            matchDataframe = {}
            #   list all all possible property names
            matchesListOfDict = [matches[key] for key in matches.keys()]
            propertyNames = set(
                [
                    key
                    for keys in [list(item.keys()) for item in matchesListOfDict]
                    for key in keys
                ]
            )
            for matchName, matchValueDict in matches.items():
                #   loop over all properties in mached
                #       and convert each match to dataframe
                # for matchPropertyName, matchPropertyValue in matchValueDict.items():
                for propertyName in propertyNames:
                    #   create or append properties value to dict of each row
                    matchPropertyDataframeDict = matchDataframe.setdefault(
                        propertyName, OrderedDict()
                    )
                    matchPropertyDataframeDict[matchName] = (
                        matchValueDict[propertyName]
                        if propertyName in matchValueDict
                        else None
                    )

            #   done, return
            if matchDataframe:
                df = DataFrame(matchDataframe)
                if not df.empty:
                    return df.convert_dtypes()
                return df
            return DataFrame([])

    def __init__(self, session, onResponseCallbackFunc=None):
        from ...factory.delivery_factory import DeliveryFactory

        config = session._get_endpoint_config("discovery.search")
        base_url = config.get_str("url")
        lookup_url = config.get_str("endpoints.lookup")
        _url = urljoin(base_url, lookup_url)

        #   session
        self._session = session

        #   callback functions
        #       on_response
        self._onResponseCallbackFunc = onResponseCallbackFunc

        #   endpoint information
        self._endpoint = DeliveryFactory.create_end_point(
            self._session, _url, self._onResponse_cb
        )

        #   store the response from endpoint request
        self._response = None

    @property
    def response(self):
        return self._response

    ###########################################################
    #   callback legacy

    def _onResponse_cb(self, endpoint, response):
        """callback when response occurred"""

        #   do call the registered callback
        self._response = response

        if self._onResponseCallbackFunc:
            #   the on response callback was registered, so call it
            # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC LOOKUP RESPONSE
            if response.is_success:
                #   success request, so parse the reponse into lookup data
                response._data = Lookup.LookupData(response.data.raw)
            self._onResponseCallbackFunc(endpoint, response)

    ###############################################################
    #   helper methods

    def _constuctBodyParameters(
        self, view, terms, scope, select, filter=None, boost=None
    ):
        """convert the python keyword arguments to the body parameters

        Returns
        -------
        dictionary
            The body parameters of a request. It's a mapping between API parameter name to value.

        """

        #   add the view this is a special because this is a require field
        parameters = {}
        parameters[self._EndPointViewParameterName] = view.value
        #       terms
        parameters[self._EndPointTermsParameterName] = terms
        #       scope
        parameters[self._EndPointScopeParameterName] = scope
        #       select
        parameters[self._EndPointSelectParameterName] = select

        #   optional
        #       filter
        if filter:
            parameters[self._EndPointFilterParameterName] = filter
        #       boost
        if boost:
            parameters[self._EndPointBoostParameterName] = boost

        #   done, return the mapping between between API parameter name to value.
        return parameters

    ###############################################################
    #   asynchronous methods

    async def _lookup_async(
        self,
        *,
        view,
        terms,
        scope,
        select,
        filter=None,
        boost=None,
        closure=None,
        extended_params=None,
    ):
        """this is a internal lookup legacy it require views, terms, scope and select.
        and keyword arguments are filter and boost.
        """

        #   construct the body data for a request
        #  parameters including view, terms, scope, select (required) and other optional arguments
        bodyParameters = self._constuctBodyParameters(
            view, terms, scope, select, filter, boost
        )
        bodyParameters.update(extended_params or {})
        #   send the request asynchronously
        response = await self._endpoint.send_request_async(
            method=Endpoint.RequestMethod.POST,
            header_parameters={"Content-Type": "application/json"},
            body_parameters=bodyParameters,
            closure=closure,
        )

        #   store the response
        # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC LOOKUP RESPONSE
        self._response = response
        if self._response.is_success:
            #   success request, so parse the reponse into lookup data
            self._response._data = Lookup.LookupData(response.data.raw)

        #   done, return response
        return self.response

    @staticmethod
    async def lookup_async(
        *,
        session=None,
        on_response=None,
        view,
        terms,
        scope,
        select,
        filter=None,
        boost=None,
        closure=None,
        extended_params=None,
    ):
        """call asynchronous lookup with parameters

        Parameters
        ----------
        session: object
            the session for calling a lookup
        on_response: legacy, optional
            a callback legacy when response from lookup requested
            default: None
        view: object
            picks a subset of the data universe to search against. see SearchViews
        terms: string
            lists the symbols to be solved
        scope: string
            identifies the symbology which 'terms' belong to
        select: string
            specifies which properties to return for each result doc
        filter: string
            supports structured predicate expressions
        boost: string
            pushes documents matching a filter expression to the top of the list
        extended_params: dict
            other optional arguments

        Returns
        -------
        object
            The response object from given lookup parameters
        """
        #   check for using default session
        from ...core.session import get_default

        session = session if session else get_default()

        #   construct lookup object and call asynchronous lookup method
        lookup = Lookup(session, onResponseCallbackFunc=on_response)
        response = await lookup._lookup_async(
            view=view,
            terms=terms,
            scope=scope,
            select=select,
            filter=filter,
            boost=boost,
            closure=closure,
            extended_params=extended_params,
        )

        #   done, return response
        return response

    ###############################################################
    #   synchronous methods

    @staticmethod
    def lookup(
        *,
        session=None,
        on_response=None,
        view,
        terms,
        scope,
        select,
        filter=None,
        boost=None,
        extended_params=None,
    ):
        """call synchronous lookup with given parameters

        Parameters
        ----------
        session: object
            the session for calling a lookup
        on_response: legacy, optional
            a callback legacy when response from lookup requested
            default: None
        view: object
            picks a subset of the data universe to search against. see SearchViews
        terms: string
            lists the symbols to be solved
        scope: string
            identifies the symbology which 'terms' belong to
        select: string
            specifies which properties to return for each result doc
        filter: string
            supports structured predicate expressions
        boost: string
            pushes documents matching a filter expression to the top of the list
        extended_params: dict
            other optional arguments

        Returns
        -------
        object
            The response object from given lookup parameters
        """
        #   check for using default session
        from ...core.session import get_default

        session = session if session else get_default()

        #   construct lookup object and call asynchronous lookup method
        lookup = Lookup(session, onResponseCallbackFunc=on_response)
        asyncio.get_event_loop().run_until_complete(
            lookup._lookup_async(
                view=view,
                terms=terms,
                scope=scope,
                select=select,
                filter=filter,
                boost=boost,
                extended_params=extended_params,
            )
        )

        #   done, return response
        return lookup.response


class Definition:
    """
    This class describe parameters to retrieve data for search lookup.

    Parameters
    ----------

    view : SearchViews
        picks a subset of the data universe to search against. see SearchViews

    terms : str
        lists the symbols to be solved

    scope : str
        identifies the symbology which 'terms' belong to

    select : str
        specifies which properties to return for each result doc

    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
    >>> from refinitiv.data.content import search
    >>> definition = search.lookup.Definition(
    >>>     view=search.SearchViews.SEARCH_ALL,
    >>>     scope="RIC",
    >>>     terms="A,B,NOSUCHRIC,C,D",
    >>>     select="BusinessEntity,DocumentTitle"
    >>>)
    """

    def __init__(
        self,
        view: SearchViews,
        terms: str,
        scope: str,
        select: str,
        extended_params: dict = None,
    ):
        self._view = view
        self._terms = terms
        self._scope = scope
        self._select = select
        self._extended_params = extended_params

    def get_data(self, session: Session = None, on_response: Callable = None):
        """
        Returns a response from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        Lookup.LookupData

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import search
        >>> definition = search.lookup.Definition(
        >>>     view=search.SearchViews.SEARCH_ALL,
        >>>     scope="RIC",
        >>>     terms="A,B,NOSUCHRIC,C,D",
        >>>     select="BusinessEntity,DocumentTitle"
        >>>)
        >>> response = definition.get_data()
        """

        return Lookup.lookup(
            session=session,
            view=self._view,
            terms=self._terms,
            scope=self._scope,
            select=self._select,
            on_response=on_response,
            extended_params=self._extended_params,
        )

    async def get_data_async(
        self, session: Session = None, on_response: Callable = None
    ):
        """
        Returns a response asynchronously from the API to the library

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        on_response : Callable, optional
            Callable object to process retrieved data

        Returns
        -------
        Lookup.LookupData

        Raises
        ------
        AttributeError
            If user didn't set default session.

        Examples
        --------
        >>> from refinitiv.data.content import search
        >>> definition = search.lookup.Definition(
        >>>     view=search.SearchViews.SEARCH_ALL,
        >>>     scope="RIC",
        >>>     terms="A,B,NOSUCHRIC,C,D",
        >>>     select="BusinessEntity,DocumentTitle"
        >>>)
        >>> response = await definition.get_data_async()
        """

        response = await Lookup.lookup_async(
            session=session,
            view=self._view,
            terms=self._terms,
            scope=self._scope,
            select=self._select,
            on_response=on_response,
            extended_params=self._extended_params,
        )
        return response

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content.search",
            content=f"{{view='{self._view}', terms='{self._terms}', scope='{self._scope}', select='{self._select}'}}",
        )
