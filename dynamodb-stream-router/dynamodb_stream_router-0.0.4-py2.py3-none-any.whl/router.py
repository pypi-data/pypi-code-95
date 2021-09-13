#!/usr/bin/env python3.8
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
import typeguard
from os import environ
from enum import Enum, auto
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    NamedTuple,
    Tuple,
    Union,
    Any,
)
from .conditions.parser import Expression
from .exceptions import (
    ConditionError,
    MultipleRouteMatches,
    UnhandledRouteException,
    HandledRouteException
)

getLogger().setLevel("INFO")

if not environ.get("TYPECHECKED"):
    typeguard.typechecked = lambda: True


class Image(Enum):
    OldImage = auto()
    NewImage = auto()


class Operations(Enum):
    REMOVE = auto()
    INSERT = auto()
    MODIFY = auto()


class StreamRecordBase(NamedTuple):
    eventName: Operations
    awsRegion: str
    eventID: str
    eventSource: str
    eventSourceARN: str
    eventVersion: str
    Keys: dict
    NewImage: dict
    OldImage: dict
    SequenceNumber: str
    SizeBytes: int
    original: dict
    StreamViewType: str = "NEW_AND_OLD_RECORDS"


class Halt:
    """
    If a route returns an instance of ``Halt`` the route resolution will stop for the current record
    being processed. All other records will continue to be processed as usual.
    """
    pass


class StreamRecord(StreamRecordBase):
    """
    .. _dynamodb_stream_router.router.StreamRecord:

    Creates a properly formatted record to be consumed by `dynamodb_stream_router.router.StreamRouter`_
    or `dynamodb_stream_router.conditions.Expression`_


    :properties:
        * *eventName:* (``str``): MODIFY | INSERT | DELETE
        * *StreamViewType:* (``str``): NEW_AND_OLD_IMAGES by default
        * *awsRegion:* (``str``)
        * *eventID:* (``str``)
        * *eventSource:* (``str``)
        * *eventSourceARN:* (``str``)
        * *eventVersion:* (``str``)
        * *Keys:* (``dict``)
        * *NewImage:* (``dict``)
        * *OldImage:* (``dict``)
        * *SequenceNumber:* (``str``)
        * *SizeBytes:* (``int``)
        * *original:* (``dict``): The original, unserialized record

    :Arguments:
        * *record:* (``dict``):  A single record from a Dynamodb stream event

    :returns:
        `dynamodb_stream_router.router.StreamRecord`_
    """
    def __new__(cls, record: dict):
        if "dynamodb" in record:
            for k in [
                "NewImage",
                "OldImage",
                "StreamViewType",
                "SequenceNumber",
                "SizeBytes",
            ]:

                if k in record["dynamodb"]:
                    if k in ("OldImage", "NewImage"):
                        record[k] = parse_image(record["dynamodb"][k])
                    else:
                        record[k] = record["dynamodb"][k]

            del record["dynamodb"]

        defaults = {
            "awsRegion": "",
            "eventID": "",
            "eventSource": "aws:dynamodb",
            "eventSourceARN": "",
            "eventVersion": "",
            "Keys": {},
            "OldImage": {},
            "NewImage": {},
            "SequenceNumber": "",
            "SizeBytes": 0
        }

        record = {
            "original": record,
            **defaults,
            **record
        }

        try:
            record["eventName"] = Operations[record.get("eventName")].name
        except KeyError:
            raise TypeError(f"Unknown eventName {record['eventName']}'")

        return super().__new__(cls, **record)


class ExceptionHandler(NamedTuple):
    """
    .. _dynamodb_stream_router.router.ExceptionHandler:

    Provides a mechanism for attaching a callable to either the router or a specific route. When a route's callable
    raises an exception and the route or router has `exception_handler` set, then the handler will be passed the record
    and exception that was raised by the route's callable as arguments IF the exception is of a type in `ExceptionHandler.exceptions`.
    Nothing is done with the return value of the handler


    Example Usage:

    .. highlight:: python
    .. code-block:: python

        from dynamodb_stream_router import StreamRouter, ExceptionHandler
        from logging import getLogger


        def error_handler(record, error):
            print(record)
            print(error)

        router = StreamRouter()
        router.exception_handler = ExceptionHandler(
            handler=error_handler,
            exceptions=(KeyError, ValueError)
        )


        @router.modify(condition_expression="$OLD.foo == True")
        def handle_foo(record):
            # Will trigger error_handler() to print the record and exception
            raise ValueError("Caught an exception in handle_foo")


        def handler(event, ctx):
            router.resolve_all(event["Records"])


    """

    #: The callable that will be passed the original record and exception raised by the route callable that raised the exception
    handler: Callable[[StreamRecord, Union[Exception, Any]], Any]
    #: A tuple of exception types to catch
    exceptions: Tuple[Union[Exception, Any]]


class Route(NamedTuple):
    """
    .. _dynamodb_stream_router.router.Route:

    A route object to be registered into an instance of `dynamodb_stream_router.router.StreamRouter`_
    See the following for usage:

        * `dynamodb_stream_router.router.StreamRouter.insert`_
        * `dynamodb_stream_router.router.StreamRouter.remove`_
        * `dynamodb_stream_router.router.StreamRouter.modify`_
        * `dynamodb_stream_router.router.StreamRouter.Route`_

    """
    #: The Callable that will be triggered if this route is a match for a record
    callable: Callable
    #: The operations that this route is registered for (MODIFY | INSERT | DELETE)
    operations: List[Operations]
    #: Optional `dynamodb_stream_router.conditions.Expression`_ string or Callable to be used for route matching
    condition_expression: Union[Callable, str] = None
    #: Optional Priority to assign to this route. All routes that match a record will be called in order of priority
    priority: int = 0
    #: Optional flag to indicate record processing should stop after this route is called
    halt: bool = False
    #: Optional flat that indicates whether to halt all processing if a route raises an exception. If True then the exception will be raised, if False the exception will be placed in Result.error
    halt_on_exception: bool = False
    #: Optional callable that will be passed the record and exception that was raised in the case that the route's callable raises an exception
    exception_handler: ExceptionHandler = None


class Result(NamedTuple):
    """
    .. _dynamodb_stream_router.router.Result:

    The result returned by a route called by `dynamodb_stream_router.router.StreamRouter`_
    """
    #: The complete `dynamodb_stream_router.router.Route`_  object that generated this result
    route: Route
    #: The original stream record passed to the Route's callable
    record: dict
    #: The return value of the callable for the Route that was called
    value: Any = None
    #: Any errors that were raised during the route's callable's execution
    error: Union[HandledRouteException, UnhandledRouteException] = None


class RouteSet(NamedTuple):
    REMOVE: List[Route]
    INSERT: List[Route]
    MODIFY: List[Route]


class StreamRouter:
    """
    .. _dynamodb_stream_router.router.StreamRouter:

    Provides routing of Dynamodb Stream records to Callables based on record eventName and an optional condition, expressed
    as a string to be evaluated by `dynamodb_stream_router.conditions.parser.Expression.parse`_ or a truthy function that receives
    the record as its sole argument.

    :Keyword Arguments:
        * *threaded:* (``bool``): If True then each record will be processed in a separate thread using ThreadPoolExecutor
        * *threads:* (``int``): Max number of threads for ThreadPoolExecutor. Only applies if *threaded=True*
        * *allow_multiple_matches:* (``bool``): Optional flag indicating whether or not to allow multiple route matches
          for a record. If True and multiple routes match a record then ``dynamodb_stream_router.exceptions.MultipleRouteMatches``
          will be raised. Useful if continuing to process a record after an unintended route match could cause problems in your
          application


    Intelligently decides what Callable to invoke for a given record based on the StreamRecord's eventName and optional conditions in the form
    of callables or a condition expression that is parsed by `dynamodb_stream_router.conditions.Expression`_ . Decorators are used to register callables
    as Route(s).

    Example Usage:

    .. highlight:: python
    .. code-block:: python

        from dynamodb_stream_router.router import Record, StreamRouter

        router = StreamRouter()

        records = [{
                "StreamViewType": "NEW_AND_OLD_IMAGES",
                "eventName": "MODIFY",
                "dynamodb": {
                    "OldImage": {
                        "type": {
                            "M": {
                                "foo": {
                                    "M": {
                                        "bar": {
                                            "L": [
                                                {"S": "baz"}
                                            ]
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "NewImage": {
                        "type": {"S": "sometype"}
                    }
                }
            }]

        @router.modify(condition_expression="has_changed('type')")
            def my_first_route(record):
                return True

            res = router.resolve_all(records)


    In the example above the function * my_first_route() * will be called because * record.OldImage["type"] * has changed in comparison to * record.NewImage["type"].
    This example uses `dynamodb_stream_router.conditions.Expression`_ as the condition_expression used to match the route to the record. In addition to passing
    a string-based expression you could pass your own callable, for instance a lambda, that accepts * record * as its only required argument and returns a bool
    indicating whether or not the route matches.

    Example using a lambda as condition_expression:

    .. highlight:: python
    .. code-block:: python

        from dynamodb_stream_router.router import StreamRouter

        router = StreamRouter()

        @router.modify(condition_expression=lambda x: x.OldImage["type"] != x.NewImage["type"])
        def my_first_route(record):
                return True

            res = router.resolve_all(records)


    The second example(assuming we used the same list of records) would have the same result as the first
    """
    __instance = None
    __threads = 0
    __threaded = False
    __executor = None

    def __new__(
        cls,
        *args,
        threads: int = None,
        threaded: bool = False,
        allow_multiple_matches: bool = True,
        exception_handler: ExceptionHandler = None,
        halt_on_exception: bool = True,
        **kwargs
    ):
        if not threaded and threads is not None:
            raise AttributeError(
                "Argument 'threads' doesn't make sense if 'threaded=False'"
            )

        if threads == 0:
            raise AttributeError("Number of threads must be > 0")

        if cls.__instance is None:
            cls.__threads = threads or 0
            cls.__threaded = threaded or bool(threads)
            if threads:
                cls.__executor = ThreadPoolExecutor(max_workers=threads)
            elif threaded:
                cls.__executor = ThreadPoolExecutor()

            cls.__instance = super().__new__(cls, *args, **kwargs)

        return cls.__instance

    def __init__(self, *args, **kwargs):

        #: A list of dynamodb_stream_router.Route that are registered to the router
        self.routes: RouteSet = RouteSet(**{"REMOVE": [], "INSERT": [], "MODIFY": []})
        #: Whether or not to allow multiple routes to be called on a single record. If False and multiple routes are found for a record an exception will be raised
        self.allow_multiple_matches: bool = kwargs.get("allow_multiple_matches", True)

        #: If defined then a route handler that raises an exception defined in exception_handler will have its record, and the exception, passed to exception_handler.handler
        self.exception_handler: ExceptionHandler = kwargs.get("exception_handler")

        #: If defined then a route handler that raises an exception will propagate that exception. Otherwise the exception will be placed in the result and execution will continue
        self.halt_on_exception: bool = kwargs.get("halt_on_exception")

        self._condition_parser = Expression()

    def modify(self, **kwargs) -> Callable:
        """
        .. _dynamodb_stream_router.router.StreamRouter.modify:

        Wrapper for StreamRouter.route(). Creates a route for "MODIFY" operation, taking an optional condition_expression

        :Keyword Arguments:
            * *condition_expression:* (``Union[Callable, str]``): An expression that returns a boolean indicating if
              the route should be called for a particular record. If type is ``str`` then the expression will be parsed using
              `dynamodb_stream_router.conditions.Expression`_ *parse()* method to generate the callable
            * *halt:* (``int``): Stop processing of record after this route is called. The same effect can be acheived by returning
              an object of type ``dynamodb_stream_router.router.Halt``. Default is False
            * *priority:* (``int``): The priority of this route in the list of any matching routes for a record. Default is 0

        :returns:
            ``Callable``

        Example Usage:

        .. highlight:: python
        .. code-block:: python

            from dynamodb_stream_router.router import StreamRouter


            @router.modify(condition_expression="has_changed('foo')")
            def process_foo(record):
                pass

        """
        return self.route("MODIFY", **kwargs)

    def remove(self, **kwargs) -> Callable:
        """
        .. _dynamodb_stream_router.router.StreamRouter.remove:

        Wrapper for StreamRouter.route(). Creates a route for "REMOVE" operation, taking an optional condition_expression

        :Keyword Arguments:
            * *condition_expression:* (``Union[Callable, str]``): An expression that returns a boolean indicating if
              the route should be called for a particular record. If type is ``str`` then the expression will be parsed using
              `dynamodb_stream_router.conditions.Expression`_ *parse()* method to generate the callable
            * *halt:* (``int``): Stop processing of record after this route is called. The same effect can be acheived by returning
              an object of type ``dynamodb_stream_router.router.Halt``. Default is False
            * *priority:* (``int``): The priority of this route in the list of any matching routes for a record. Default is 0

        :returns:
            ``Callable``

        Example Usage:

        .. highlight:: python
        .. code-block:: python

            from dynamodb_stream_router.router import StreamRouter


            @router.remove(condition_expression="has_changed('foo')")
            def process_foo(record):
                pass

        """
        return self.route("REMOVE", **kwargs)

    def insert(self, **kwargs) -> Callable:
        """
        .. _dynamodb_stream_router.router.StreamRouter.insert:

        Wrapper for StreamRouter.route(). Creates a route for "INSERT" operation, taking an optional condition_expression

        :Keyword Arguments:
            * *condition_expression:* (``Union[Callable, str]``): An expression that returns a boolean indicating if
              the route should be called for a particular record. If type is ``str`` then the expression will be parsed using
              `dynamodb_stream_router.conditions.Expression`_ *parse()* method to generate the callable
            * *halt:* (``int``): Stop processing of record after this route is called. The same effect can be acheived by returning
              an object of type ``dynamodb_stream_router.router.Halt``. Default is False
            * *priority:* (``int``): The priority of this route in the list of any matching routes for a record. Default is 0

        :returns:
            ``Callable``

        Example Usage:

        .. highlight:: python
        .. code-block:: python

            from dynamodb_stream_router.router import StreamRouter


            @router.insert(condition_expression="has_changed('foo')")
            def process_foo(record):
                pass

        """
        return self.route("INSERT", **kwargs)

    def route(
        self,
        operations: Union[str, List[str]],
        condition_expression: Union[Callable, str] = None,
        halt: bool = False,
        priority: int = 0,
        exception_handler: ExceptionHandler = None,
        halt_on_exception: bool = None
    ) -> Callable:

        """
        .. _dynamodb_stream_router.router.StreamRouter.route:

        Used as a decorator to register a route. Accepts keyword arguments that determine under what conditions the route will
        be called. If no condition_expression is provided then the route will be called for any operations that are
        passed.

        :Keyword Arguments:
            * *operations:* (``Union[str, List[str]``): A Dynamodb operation or list of operations. Can be one or
              more of 'REMOVE | INSERT | MODIFY'
            * *condition_expression:* (``Union[Callable, str]``): An expression that returns a boolean indicating if
              the route should be called for a particular record. If type is ``str`` then the expression will be parsed using
              `dynamodb_stream_router.conditions.Expression`_ *parse()*  to generate the callable
            * *halt:* (``int``): Stop processing of record after this route is called. The same effect can be acheived by returning
              an object of type ``dynamodb_stream_router.router.Halt``. Default is False
            * *priority:* (``int``): The priority of this route in the list of any matching routes for a record. Default is 0
            * *halt_on_exception:* (``bool``): If True and a route's callable raises an exception then the exception will be propagated,
              otherwise the exception will be caught and placed in Result.error
            * *exception_handler:* (``ExceptionHandler`` ): An instance of `dynamodb_stream_router.router.ExceptionHandler`_ that, if a
              route's callable raises an exception AND the exception is of one of the types in exception_handler.exceptions, will have
              its handler called with the record and exception that was raised passed as arguments. Nothing is done with the return
              value of the handler and if `halt_on_exception` is set then the original exception will still be propagated


        :returns:
            ``Callable``

        Example Usage:

        .. highlight:: python
        .. code-block:: python

            from dynamodb_stream_router.router import StreamRouter


            @router.route(["MODIFY", "INSERT", "DELETE"], condition_expression="has_changed('foo')")
            def process_foo_any(record):
                pass


            @router.route(["INSERT", "DELETE"], condition_expression="has_changed('bar')")
            def process_bar_new_and_delete(record):
                pass


            @router.route(["INSERT"], condition_expression="has_changed('baz')")
            def process_new_baz(record):
                pass

        """
        known_operations = [x.name for x in Operations]

        if not isinstance(operations, list):
            operations = [operations]

        for op in operations:
            if op not in known_operations:
                raise TypeError(
                    "Supported operations are 'REMOVE', 'INSERT', and 'MODIFY'"
                )

        def inner(func: Callable) -> Callable:
            route = Route(
                operations=operations,
                callable=func,
                condition_expression=condition_expression,
                priority=priority,
                halt=halt,
                exception_handler=exception_handler,
                halt_on_exception=halt_on_exception
            )

            for x in route.operations:
                self.routes._asdict()[x].append(route)

            return func

        return inner

    @property
    def threaded(self) -> bool:
        """
        Whether or not to use parse each record in ThreadPoolExecutor

        :type: ``bool``
        """
        return self.__threaded

    @threaded.setter
    def threaded(self, val: bool):
        if val == self.__threaded:
            return
        if True and not self.__threads:
            self.__executor = ThreadPoolExecutor()
        else:
            self.__executor = ThreadPoolExecutor(max_threads=self.__threads)

    @property
    def threads(self) -> int:
        """
        Max number of threads to use in ThreadPoolExecutor.  If self.threaded = False
        then setting this will also set self.threaded to True. If self.threaded = True,
        then setting this to a non-zero value will set it to False

        :type: ``int``

        """
        return self.__threads or 0

    @threads.setter
    def threads(self, val: int):
        if val == self.__threads:
            return

        if val == 0:
            self.__threaded = False

        else:
            self.__threaded = True
            self.__threads = val
            self.__executor = ThreadPoolExecutor(max_threads=val)

    @property
    def threaded(self) -> bool:
        """
        If True, then each record will be handled in its own thread using ThreadPoolExecutor

        :type: ``bool``
        """
        return bool(self.__threads)

    def resolve_all(self, records: List[dict]) -> List[Result]:
        """
        Iterates through each record in a batch and calls any matching resolvers on them, returning a
        list containing ``Result`` objects for any routes that were called on the records. If a route is called
        on a record, and the route was created with ``halt=True`` or the route returns ``dynamodb_stream_router.router.Halt()``
        then no further routes will be called on that record. Processing of other records will continue as normal.

        :Arguments:
            * *records:* (``List[dict]``): List of Dynamodb stream records to process. Normally you would pass ``event["Records"]``

        :returns:
            List[`dynamodb_stream_router.router.Result`_ ]
        """
        self.records = [StreamRecord(x) for x in records]

        if self.threads:
            res = self.__executor.map(self.resolve_record, self.records)
        else:
            res = map(self.resolve_record, self.records)

        results = []
        for x in res:
            results += x

        return results

    def resolve_record(self, record: StreamRecord) -> List[Result]:
        """
        Resolves a single record, returning a list containing ``Result`` objects for any
        routes that were called on the record

        :Arguments:
            * *record:* (``dict``): A single stream record

        :returns:
            List[`dynamodb_stream_router.router.Result`_ ]
        """

        routes_to_call = []
        op = record.eventName

        for route in self.routes._asdict()[op]:
            if route.condition_expression is None:
                routes_to_call.append(route)

            else:
                if isinstance(route.condition_expression, str):
                    try:
                        test = self._condition_parser.evaluate(
                            route.condition_expression, record=record
                        )
                    except Exception as e:
                        raise ConditionError(
                            f"Could not parse {route.condition_expression}: {e}") from e
                else:
                    try:
                        test = route.condition_expression(record)
                    except Exception as e:
                        raise ConditionError(f"Could not parse expression using {route.condition_expression}") from e

                if test:
                    routes_to_call.append(route)

        routes_to_call.sort(key=lambda x: x.priority)
        num_of_routes = len(routes_to_call)
        getLogger().info(f"Found {num_of_routes} routes for {record._asdict()}")

        if not self.allow_multiple_matches and num_of_routes > 1:
            raise MultipleRouteMatches(f"Multiple routes matched for record {record._asdict}")

        results = []
        for route in routes_to_call:
            result = self.__execute_route(route, record)

            if result.error and (
                route.halt_on_exception
                or self.halt_on_exception
            ):
                raise result.error

            results.append(result)

            if route.halt or isinstance(result, Halt):
                break

        return results

    def __execute_route(self, route, record):
        if handler := (route.exception_handler or self.exception_handler):
            exceptions = handler.exceptions
            returned_exception = HandledRouteException
            handler = handler.handler
        else:
            exceptions = Exception
            returned_exception = UnhandledRouteException
            handler = None

        result = {
            "route": route,
            "record": record,
            "value": None,
            "error": None
        }

        try:
            result["value"] = route.callable(record)
        except exceptions as e:
            if handler:
                handler(record, e)

            result["error"] = returned_exception(e)

        return Result(**result)


def parse_image(image: dict):
    if isinstance(image, dict):
        is_single = True
        items = [image]
    else:
        items = image
        is_single = False

    def parseList(dynamoList):
        i = 0
        for d in dynamoList:
            dynamoType = list(d.keys())[0]
            dynamoList[i] = typeMap[dynamoType](d[dynamoType])
            i += 1
        return dynamoList

    def parseMap(dynamoMap):
        for d in dynamoMap:
            dynamoType = list(dynamoMap[d].keys())[0]
            dynamoMap[d] = typeMap[dynamoType](dynamoMap[d][dynamoType])
        return dynamoMap

    typeMap = {
        "S": lambda x: x,
        "N": lambda x: x,
        "L": parseList,
        "B": lambda x: bytes(x.encode()),
        "BS": parseList,
        "BOOL": lambda x: x,
        "NS": parseList,
        "NULL": lambda x: None,
        "SS": parseList,
        "M": parseMap,
    }

    i = 0
    for item in items:
        newItem = {}
        for attributeName in item.keys():
            dynamoType = next(iter(item[attributeName]))
            val = typeMap[dynamoType](item[attributeName][dynamoType])
            newItem[attributeName] = val

        items[i] = newItem
        i += 1

    if is_single:
        items = items[0]

    return items
