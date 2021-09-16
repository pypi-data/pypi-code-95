# coding: utf8

__all__ = ["Definition"]

from typing import Optional

from ..data_grid._fundamental_class import Fundamental
from ... import Session
from ...tools._repr_definition import create_str_definition


class Definition:
    """
    This class describe the universe (list of instruments), the fields (a.k.a. data items) and
    parameters that will be requested to the data platform

    Parameters:
    ----------
    universe : list
        The list of RICs
    fields : list
        List of fundamental field names
    parameters : dict, optional
        Global parameters for fields
    field_name : str, optional
        Field name provided by user to use field titles of field names
    closure : str, optional
        Specifies the parameter that will be merged with the request
    extended_params : dict, optional
        Other parameters can be provided if necessary

    Examples
    --------
    >>> from refinitiv.data.content import fundamental_and_reference
    >>> definition = fundamental_and_reference.Definition(["IBM"], ["TR.Volume"])
    """

    def __init__(
        self,
        universe: list,
        fields: list,
        parameters: Optional[dict] = None,
        field_name: Optional[str] = None,
        closure: Optional[str] = None,
        extended_params: Optional[dict] = None,
    ):
        self.universe = universe
        self.fields = fields
        self.parameters = parameters
        self.field_name = field_name
        self.closure = closure
        self.extended_params = extended_params

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content",
            content=f"{{name='{self.universe}'}}",
        )

    def get_data(self, session: Session = None, on_response=None):
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
        Response

        Examples
        --------
        >>> from refinitiv.data.content import fundamental_and_reference
        >>> definition = fundamental_and_reference.Definition(["IBM"], ["TR.Volume"])
        >>> definition.get_data()
        """
        fundamental_class = Fundamental(session=session, on_response=on_response)
        response = fundamental_class._get_data(
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            field_name=self.field_name,
            closure=self.closure,
            extended_params=self.extended_params,
        )

        return response

    async def get_data_async(self, session: Session = None, on_response=None):
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
        Response

        Examples
        --------
        >>> from refinitiv.data.content import fundamental_and_reference
        >>> definition = fundamental_and_reference.Definition(["IBM"], ["TR.Volume"])
        >>> await definition.get_data_async()
        """
        fundamental_class = Fundamental(session=session, on_response=on_response)
        response = await fundamental_class._get_data_async(
            universe=self.universe,
            fields=self.fields,
            parameters=self.parameters,
            field_name=self.field_name,
            closure=self.closure,
            extended_params=self.extended_params,
        )
        return response
