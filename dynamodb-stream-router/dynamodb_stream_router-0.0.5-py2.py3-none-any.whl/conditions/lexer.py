# flake8: noqa
# pyright: reportUndefinedVariable=false
from sly import Lexer
from ..exceptions import SyntaxError


class ExpressionLexer(Lexer):
    # Set of token names.
    tokens = {
        VALUE,
        INT,
        FLOAT,
        BETWEEN,
        AND,
        OR,
        NOT,
        IN,
        EQ,
        NE,
        GT,
        GTE,
        LT,
        LTE,
        ATTRIBUTE_EXISTS,
        ATTRIBUTE_NOT_EXISTS,
        ATTRIBUTE_TYPE,
        BEGINS_WITH,
        CONTAINS,
        SIZE,
        FROM_JSON,
        OLD_IMAGE,
        NEW_IMAGE,
        NAME,
        CHANGED,
        MATCH,
        IS_TYPE,
        FALSE,
        TRUE
    }

    # Set of literal characters
    literals = {"(", ")", "[", "]", ",", "."}

    # String containing ignored characters
    ignore = " \t"

    # Regular expression rules for tokens
    OLD_IMAGE = r"\$OLD"
    NEW_IMAGE = r"\$NEW"

    AND = r"\&{1}"
    OR = r"\|{1}"
    NOT = "NOT"
    IN = "IN"
    BETWEEN = "BETWEEN"
    CHANGED = "has_changed"
    IS_TYPE = "is_type"
    ATTRIBUTE_EXISTS = "attribute_exists"
    ATTRIBUTE_NOT_EXISTS = "attribute_not_exists"
    ATTRIBUTE_TYPE = "attribute_type"
    BEGINS_WITH = "begins_with"
    CONTAINS = "contains"
    FROM_JSON = "from_json"
    SIZE = "size"
    TRUE = "True"
    FALSE = "False",

    """
    NAME has to come AFTER any keywords above. NAME is used as a path within OLD_IMAGE/NEW_IMAGE
    and also Dynamodb types such as S, L, SS, NS, BOOL, etc...
    """
    NAME = r"[a-zA-Z_][a-zA-Z0-9\-_]*"
    NE = "!="
    GTE = ">="
    LTE = "<="
    EQ = "=="
    GT = ">"
    LT = "<"
    INT = "\d+"
    MATCH = "=~"
    FLOAT = "\d+\.\d+"
    VALUE = r""""([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\'"""

    # Line number tracking
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        if t.value[0] == "$":
            raise SyntaxError(f"Invalid base path {t.value.split(' ')[0].split('.')[0]}")
        else:
            raise SyntaxError(f"Bad character '{t.value[0]}' at line {self.lineno} character {self.index}")
