# coding: utf-8

__all__ = ["Definition"]

from typing import Any, Optional, Callable

from ... import Session
from ..streaming.streamingchain import StreamingChain
from ...tools._repr_definition import create_str_definition


class Definition(object):
    """
    Class is designed to request streaming chains and decode it dynamically

    Parameters
    ----------
    universe : str
        Single instrument name
    closure : Any, optional
        Specifies the parameter that will be merged with the request

    Examples
    --------
    >>> from refinitiv.data.content.pricing import chain
    >>> definition_chain = chain.Definition("EUR")
    """

    def __init__(self, universe: str, closure: Any = None):
        self._universe = universe
        self._closure = closure

    def __repr__(self):
        return create_str_definition(
            self,
            middle_path="content",
            end_path="pricing.chain",
            content=f"{{name='{self._universe}'}}",
        )

    def get_stream(
        self,
        session: Session = None,
        service: Optional[str] = None,
        # option for chain constituents
        skip_summary_links: Optional[bool] = True,
        skip_empty: Optional[bool] = True,
        override_summary_links: Optional[int] = None,
        # callbacks
        on_add: Optional[Callable] = None,
        on_remove: Optional[Callable] = None,
        on_update: Optional[Callable] = None,
        on_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ) -> StreamingChain:
        """
        Return a chain.StreamingChain object for the defined data

        Parameters
        ----------
        session : Session, optional
            The Session defines the source where you want to retrieve your data
        service : str, optional
            Name service
        skip_summary_links : bool, optional
            Store skip summary links
        skip_empty : bool, optional
            Store skip empty
        override_summary_links : int, optional
            Store the override number of summary links
        on_add : Callable, optional
            Called when an add is received
        on_remove : Callable, optional
            Called when a remove is received
        on_update : Callable, optional
            Called when a update is received
        on_complete : Callable, optional
            Called when a complete is received
        on_error : Callable, optional
            Called when a error is received

        Returns
        -------
        chain.StreamingChain

        Examples
        -------
        Create a chain.StreamingChain object

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream()

        Open the StreamingChain connection

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream()
        >>> chain_stream.open()

        Closes the StreamingChain connection

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream()
        >>> chain_stream.open()
        >>> chain_stream.close()

        Call get_constituents

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream()
        >>> chain_stream.open()
        >>> chain_stream.get_constituents()

        Call property is_chain

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream()
        >>> chain_stream.open()
        >>> chain_stream.is_chain

        Call callback parameters

        >>> from refinitiv.data.content.pricing import chain
        >>> definition_chain = chain.Definition("EUR")
        >>> chain_stream = definition_chain.get_stream(
        on_add = lambda streaming_chain, index, constituent:
        print(f"{index}:{constituent}"),
        on_remove = lambda streaming_chain, index, constituent:
        print(f"{index}:{constituent}"),
        on_update = lambda streaming_chain, index, old_constituent, new_constituent:
        print(f"{index}:{old_constituent}:{new_constituent}"),
        on_complete = lambda streaming_chain, constituents:
        print(constituents),
        on_error = lambda streaming_chain, index, error:
        print("ERROR", error)
        )
        >>> chain_stream.open()
        """
        _stream = StreamingChain(
            name=self._universe,
            session=session,
            service=service,
            # option for chain constituents
            skip_summary_links=skip_summary_links,
            skip_empty=skip_empty,
            override_summary_links=override_summary_links,
            # callbacks
            on_add=on_add,
            on_remove=on_remove,
            on_update=on_update,
            on_complete=on_complete,
            on_error=on_error,
        )
        return _stream
