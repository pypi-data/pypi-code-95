#!/usr/bin/env python3.8
# pyright: reportUndefinedVariable=false
from typing import TYPE_CHECKING
from simplejson import loads
from sly import Parser
from sly.yacc import YaccProduction
from re import match
from typing import Callable
from .lexer import ExpressionLexer
from ..exceptions import (
    SyntaxError,
    KeywordError
)

if TYPE_CHECKING:
    from ..router import StreamRecord
else:
    StreamRecord = object


def is_bytes(val):
    return isinstance(val, bytes)


def is_bs(val):
    return isinstance(val, list) and [x for x in val if isinstance(val, bytes)]


def is_ss(val):
    return isinstance(val, list) and [x for x in val if isinstance(val, str)]


def is_ns(val):
    return isinstance(val, list) and [
        x for x in val if isinstance(val, (int, float))
    ]


def is_l(val):
    if not isinstance(val, list):
        return False

    first_type = type(val)
    for x in val[1:]:
        if type(x) != first_type:
            return False

    return True


def is_bool(val):
    return type(val, bool)


def is_null(val):
    return val is None


def is_str(val):
    return isinstance(val, str)


def is_m(val):
    return isinstance(val, dict)


class Expression(Parser):
    r"""
    .. _dynamodb_stream_router.conditions.Expression:

    Used to build an expression from a string that, when passed to the evaluation method, will return a bool
    by executing the statements in the expression against a `dynamodb_stream_router.router.StreamRecord`_.
    Example of testing an expression directly:

    .. highlight:: python
    .. code-block:: python

        from dynamodb_stream_parser.conditions.parser import Expression
        from dynamodb_stream_router.router import StreamRouter, Record


        router = StreamRouter(threaded=True)

        item = {
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
        }

        parser = Expression()
        exp = "$NEW.type == 'sometype' & has_changed('type')"
        res = exp.evaluate(exp, record=Record(item))
        print(exp.evaluate())
        # Prints 'True'


        ''' Using an expression with StreamRouter '''
        from dynamodb_stream_parser.conditions.parser import Expression
        from dynamodb_stream_router.router import StreamRouter, Record

        router = StreamRouter()
        exp = "$NEW.type == 'sometype' & has_changed('type')


        @router.update(condition_expression=exp)
        def func_name(item):
            return 1


        records = [StreamRecord(item)]

        res = router.resolve_all(items)
        print([x.value for x in res])

        # prints '[1]'


    More about using `dynamodb_stream_router.router.StreamRouter`_

    .. list-table:: Identifiers
        :widths: 10 25 25
        :header-rows: 1

        * - Type
          - Description
          - Example
        * - VALUE
          - A quoted string (single or double), integer, or float representing a literal value
          - 'foo'
        * - $OLD
          - A reference to StreamRecord.OldImage
          - $OLD.foo
        * - $NEW
          - A reference to StreamRecord.NewImage
          - $NEW.bar
        * - PATH
          - A path inside of a StreamRecord. Paths always start with $OLD or $NEW
          - $OLD.foo.bar or $OLD["foo"]["bar"] or $NEW.foo[0]
        * - INDEX
          - A numeric index into a PATH where PATH is a List
          - $OLD.foo[0]
        * - Key
          - A python-style key reference within a PATH
          - $OLD["foo"]


    .. list-table:: Operators
        :widths: 10 25
        :header-rows: 1

        * - Operator
          - Action
        * - &
          - Logical AND
        * - \|
          - Logical OR
        * - ()
          - Grouping of expressions
        * - ==
          - Equality
        * - !=
          - Non equality
        * - >
          - Greater than
        * - >=
          - Greater than or equal to
        * - <
          - Less than
        * - <=
          - Less than or equal to
        * - =~
          - Regex comparison <value> =~ <regex>


    Comparison operators, except for regex comparison, can compare PATH to VALUE, PATH to PATH, or even VALUE to VALUE.


    .. list-table:: Functions
        :widths: 20 20 50
        :header-rows: 1

        * - Name
          - Arguments
          - Description
        * - has_changed(VALUE, VALUE)
          - Comma-separated list of quoted values
          - Tests each value to see if that key in the top level of $OLD differs from $NEW. Returns True if any of the elements have changed
        * - is_type(PATH, TYPE)
          - PATH - The path to a value to test and the Dynamodb type to test for, TYPE - Any Dynamodb Type
          - Returns if PATH is of type TYPE. TYPE can be any unquoted Dynamodb type (S, SS, B, BS, N, NS, M, BOOL, L)
        * - attribute_exists(PATH)
          - PATH - An element to test the existence of
          - Returns a bool indicating if the specified key/index exists in PATH
        * - from_json(PATH)
          - PATH - A path to decode
          - Returns a value returned from simplejson.loads()
    """

    _expression_cache = {}

    # Get the token list from the lexer (required)
    tokens = ExpressionLexer.tokens

    # Define precendence
    precedence = (
        ("left", OR),  # noqa: 821
        ("left", AND),  # noqa: 821
        ("right", NOT),  # noqa: 821
        ("nonassoc", EQ, NE, GT, LT, LTE, GTE),  # noqa: 821
    )

    def __init__(self, record: StreamRecord = None):
        self.__record = None
        self.__old_image = None
        self.__new_image = None
        self.__old_keys = None
        self.__new_keys = None
        if record is not None:
            self.record = record
        super().__init__()

    def evaluate(self, expression, record: StreamRecord = None) -> bool:
        """
        Evaluates an expression against a StreamRecord, returning the resulting bool

        :Arguments:
          * *expression:* (``str``): The expression to evaluate

        :Keyword Arguments:
            * *record:* (`dynamodb_stream_router.router.StreamRecord`_): The record to evaluate against. If not provided then self.record will be used. If self.record is None TypeError will be raised

        :returns:
            ``bool``
        """

        record = record or self.record
        if record is None:
            raise TypeError("Expression().record must be set or 'record' passed to evaluate.")

        if callable(expression):
            return expression(record or self.record)
        else:
            try:
                return self.parse(expression)(record or self.record)
            except TypeError as e:
                if str(e) == "'NoneType' object is not callable":
                    raise SyntaxError("Illegal condition statement")

    def parse(self, expression: str) -> Callable:
        """
        .. _dynamodb_stream_router.conditions.parser.Expression.parse:

        Takes an expression string and returns a function, which can evaluate against a record

        :Arguments:
            * *expression*: (``str``): An expressions as a string to parse

        :returns:
            ``Callable``
        """
        if expression not in self._expression_cache:
            self._expression_cache[expression] = super().parse(
                ExpressionLexer().tokenize(expression)
            )
        return self._expression_cache[expression]

    @property
    def old(self) -> dict:
        """
        Shorthand for ``self.record.OldImage``

        :returns:
            ``dict``
        """
        return self.__old_image

    @property
    def new(self) -> dict:
        """
        Shorthand for ``self.record.NewImage``

        :returns:
            ``dict``
        """
        return self.__new_image

    @property
    def old_keys(self) -> list:
        """
        Shorthand for ``list(self.record.OldImage.keys())``

        :returns:
            ``list``
        """
        return self.__old_keys

    @property
    def new_keys(self) -> list:
        """
        Shorthand for ``list(self.record.NewImage.keys())``

        :returns:
            ``list``
        """
        return self.__new_keys

    @property
    def record(self) -> StreamRecord:
        """
        The StreamRecord to evaluate against

        :returns:
            `dynamodb_stream_router.router.StreamRecord`_
        """
        return self.__record

    @staticmethod
    def _strip_quotes(val: str) -> str:
        return val[1:-1]

    @record.setter
    def record(self, record: StreamRecord) -> None:
        self.__old_image = record.OldImage
        self.__new_image = record.NewImage
        self.__old_keys = list(record.OldImage.keys())
        self.__new_keys = list(record.NewImage.keys())
        self.__record = record

    # Grammar rules and actions
    @_("operand EQ operand")  # noqa: 821
    def condition(self, p):
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) == operand1(m)

    @_("operand NE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) != operand1(m)

    @_("operand GT operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) > operand1(m)

    @_("operand GTE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) >= operand1(m)

    @_("operand LT operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) < operand1(m)

    @_("operand LTE operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: operand0(m) <= operand1(m)

    @_("operand BETWEEN operand AND operand")  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        operand2 = p.operand2
        return lambda m: operand1(m) <= operand0(m) <= operand2(m)

    @_('operand IN "(" in_list ")"')  # noqa: 821
    def condition(self, p):  # noqa: 811
        operand = p.operand
        in_list = p.in_list
        return lambda m: operand(m) in in_list(m)

    @_("function")  # noqa: 821
    def condition(self, p):  # noqa: 811
        function = p.function
        return lambda m: function(m)

    @_("condition AND condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return lambda m: condition0(m) and condition1(m)

    @_("condition OR condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition0 = p.condition0
        condition1 = p.condition1
        return lambda m: condition0(m) or condition1(m)

    @_("NOT condition")  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition = p.condition
        return lambda m: not condition(m)

    @_("NOT path")  # noqa: 821
    def condition(self, p):  # noqa: 811
        return lambda m: not p.path(m)

    @_('"(" condition ")"')  # noqa: 821
    def condition(self, p):  # noqa: 811
        condition = p.condition
        return lambda m: condition(m)

    @_('ATTRIBUTE_EXISTS "(" path ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        return lambda m: path(m) is not None

    @_('ATTRIBUTE_NOT_EXISTS "(" path ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        return lambda m: path(m) is None

    @_('ATTRIBUTE_TYPE "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return lambda x: path, operand

    @_('BEGINS_WITH "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return (
            lambda m: path(m).startswith(operand(m))
            if isinstance(path(m), str)
            else False
        )

    @_('CONTAINS "(" path "," operand ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path
        operand = p.operand
        return (
            lambda m: operand(m) in path(m)
            if isinstance(path(m), (str, set))
            else False
        )

    @_('SIZE "(" path ")"')  # noqa: 821
    def operand(self, p):  # noqa: 811
        path = p.path
        return (
            lambda m: len(path(m))
            if isinstance(path(m), (str, set, dict, bytearray, bytes, list))
            else -1
        )

    @_('in_list "," operand')  # noqa: 821
    def in_list(self, p):  # noqa: 811
        in_list = p.in_list
        operand = p.operand
        return lambda m: [*in_list(m), operand(m)]

    @_('operand "," operand')  # noqa: 821
    def in_list(self, p):  # noqa: 811
        operand0 = p.operand0
        operand1 = p.operand1
        return lambda m: [operand0(m), operand1(m)]

    @_("path")  # noqa: 821
    def operand(self, p):  # noqa: 811
        return p.path

    @_("VALUE")  # noqa: 821
    def operand(self, p):  # noqa: 811
        VALUE = p.VALUE
        if VALUE.startswith("'"):
            VALUE = VALUE.replace(r"\'", "'")
        else:
            VALUE = VALUE.replace(r'\"', '"')

        return lambda m: self._strip_quotes(VALUE)

    @_('operand MATCH operand')  # noqa: 821
    def condition(self, f):  # noqa: 811
        regex = f.operand1
        str_to_match = f.operand0
        return lambda x: bool(match(regex(x), str_to_match(x)))

    @_('path "." NAME')  # noqa: 821
    def path(self, p):  # noqa: 811
        path = p.path
        NAME = p.NAME
        return lambda m: path(m).get(NAME) if isinstance(path(m), dict) else None

    @_('path "[" VALUE "]"')  # noqa: 821
    def path(self, p):  # noqa: 811
        key = self._strip_quotes(p.VALUE)
        path = p.path

        return lambda m: path(m).get(key) if isinstance(path(m), dict) else None

    @_('path "[" INT "]"')  # noqa: 821
    def path(self, p):  # noqa: 811
        path = p.path
        INT = int(p.INT)
        return lambda m: path(m)[INT] if isinstance(path(m), list) and len(path(m)) >= INT else None

    @_('path "[" FLOAT "]"')  # noqa: 821
    def path(self, p):  # noqa: 811
        path = p.path
        FLOAT = float(p.FLOAT)
        return (
            lambda m: path(m)[FLOAT]
            if isinstance(path(m), list) and len(path(m)) >= FLOAT
            else None
        )

    @_("INT")  # noqa: 821
    def operand(self, o):  # noqa: 811
        INT = int(o.INT)
        return lambda m: INT

    @_("TRUE")  # noqa: 821
    def operand(self, o):  # noqa: 811
        return lambda m: True

    @_("FALSE")  # noqa: 821
    def operand(self, o):  # noqa: 811
        return lambda m: False

    @_("FLOAT")  # noqa: 821
    def path(self, p):  # noqa: 811
        FLOAT = float(p.FLOAT)
        return lambda m: FLOAT

    @_("NEW_IMAGE")  # noqa: 821
    def path(self, _):  # noqa: 811
        return lambda m: m.NewImage

    @_("OLD_IMAGE")  # noqa: 821
    def path(self, _):  # noqa: 811
        return lambda m: m.OldImage

    @_("NAME")  # noqa: 821
    def path(self, p):  # noqa: 811
        NAME = p.NAME
        if isinstance(p, YaccProduction):
            raise KeywordError(f"Unknown keyword {p.NAME}")
        return lambda m: m.get(NAME) if p(m) is not None else None

    @_('FROM_JSON "(" path ")" ')  # noqa: 821
    def function(self, p):  # noqa: 811
        return lambda m: loads(p.path(m))

    @_('CHANGED "(" in_list ")"')  # noqa: 821
    @_('CHANGED "(" VALUE ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        # 1. Key is not in both dicts
        # 2. Key is in one and not the other
        # 3. Key is in both but the items differ
        if hasattr(p, "in_list"):
            key_list = p.in_list(p)
        else:
            key_list = [self._strip_quotes(p.VALUE)]

        def has_changed(record, keys=key_list):
            for k in keys:
                if (
                    k not in record.OldImage and k in self.NewImage
                    or k not in record.OldImage and k in record.NewImage
                    or k in record.NewImage and k in record.OldImage and record.OldImage[k] != record.NewImage[k]
                ):
                    return True

            return False

        return has_changed

    @_('IS_TYPE "(" path "," NAME ")"')  # noqa: 821
    def function(self, p):  # noqa: 811
        path = p.path

        TYPE_MAP = {
            "S": lambda m: isinstance(path(m), str),
            "L": lambda m: is_l(path(m)),
            "SS": lambda m: is_ss(path(m)),
            "BS": lambda m: is_bs(path(m)),
            "NS": lambda m: is_ns(path(m)),
            "M": lambda m: isinstance(path(m), dict),
            "B": lambda m: isinstance(path(m), bytes),
            "NULL": lambda m: path(m) is None,
            "BOOL": lambda m: isinstance(path(m), bool),
        }

        if p.NAME not in TYPE_MAP:
            raise TypeError(f"Unknown type '{p.NAME}'")

        return TYPE_MAP[p.NAME]


    @_('condition error')  # noqa: 821
    def operand(self, x):  # noqa: 811
        raise SyntaxError(f"Unexpected token '{x.error.value}'")
