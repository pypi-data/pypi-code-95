"""Implementation of individual expression types."""
import re
import typing as t

from dotty_dict import Dotty  # type: ignore

from .base import BinaryExpression  # pylint: disable=unused-import
from .base import ActionExpression, Expression, MatchExpression, UnaryExpression

################ Unary Expressions ################


class And(UnaryExpression):
    """And expression."""

    op = "and"

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate ``and`` expression."""
        res = True
        for expr in self.exprs:
            if not expr.evaluate(i_dict):
                res = False
                break
        return res

    def __repr__(self):
        """Implement `repr()`."""
        return "\n\t and ".join([repr(expr) for expr in self.exprs])


class Or(UnaryExpression):
    """Or expression."""

    op = "or"

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate ``or`` expression."""
        res = False
        for expr in self.exprs:
            if expr.evaluate(i_dict):
                res = True
                break
        return res

    def __repr__(self):
        """Implement `repr()`."""
        return "\n\t or ".join([repr(expr) for expr in self.exprs])


class Not(UnaryExpression):
    """Not expression."""

    op = "not"

    def __init__(self, exprs: t.List[Expression]) -> None:
        """Initialize Not expression.

        Args:
            exprs (t.List[Expression]): List of expressions.
        """
        if len(exprs) > 1:
            raise ValueError(
                f"Not block can only have 1 child element, found {len(exprs)}",
                "Try grouping with And or Or",
            )
        super().__init__(exprs)

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate ``not`` expression."""
        return not self.exprs[0].evaluate(i_dict)

    def __repr__(self):
        """Implement `repr()`."""
        return "not (\n\t" + "\n\t".join([repr(expr) for expr in self.exprs]) + "\n)"


################ Binary Expressions ################


class Contains(MatchExpression):
    """Is expression."""

    op = "contains"

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        val = self.get_value(i_dict)
        return self.value in val

    def __repr__(self):
        """Implement `repr()`."""
        return f"{self.value} is in {self._field}"


class Is(MatchExpression):
    """Is expression."""

    op = "is"

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        val = self.get_value(i_dict)
        return val == self.value

    def __repr__(self):
        """Implement `repr()`."""
        return f"{self._field} is {self.value}"


class In(MatchExpression):
    """In expression."""

    op = "in"

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        val = self.get_value(i_dict)
        return val in self.value

    def __repr__(self):
        """Implement `repr()`."""
        return f"{self._field} is in {self.value}"


class Exists(MatchExpression):
    """Exists expression."""

    op = "exists"

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        return self.field in i_dict if self.value else self.field not in i_dict

    def __repr__(self):
        """Implement `repr()`."""
        return self._field + (" exists" if self.value else " doesn't exist")


class Regex(MatchExpression):
    """Regex expression."""

    op = "regex"

    @staticmethod
    def validate(
        field: str,
        val: t.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
        **kwargs,
    ) -> t.List[str]:
        """Validate `case-insensitive` for regex."""
        err = super(Regex, Regex).validate(field, val, variables, **kwargs)
        if "case-sensitive" in kwargs and not isinstance(
            kwargs["case-sensitive"], bool
        ):
            err.append(
                "Regex case-sensitive must be boolean, found "
                f"'{kwargs['case-sensitive']}'"
            )
        return err

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        if "case-sensitive" in self.config and self.config["case-sensitive"]:
            regex = re.compile(self.value)
        else:
            regex = re.compile(self.value, re.IGNORECASE)
        val = self.get_value(i_dict)
        return bool(regex.search(val))

    def __repr__(self):
        """Implement `repr()`."""
        return f"{self._field} matches regex {self.value}"


class Startswith(MatchExpression):
    """Startswith expression."""

    op = "startswith"

    def matches(self, i_dict: Dotty) -> bool:
        """Evaluate match."""
        regex = re.compile(f"^{self.value}")
        val = self.get_value(i_dict)
        return bool(regex.match(val))

    def __repr__(self):
        """Implement `repr()`."""
        return f"{self._field} starts with {self.value}"


################ Action Expressions ################


class Set(ActionExpression):
    """Set expression."""

    op = "set"

    def apply(self, i_dict: Dotty) -> bool:
        """Evaluate action."""
        i_dict[self.field] = self.value
        return True

    def __repr__(self):
        """Implement `repr()`."""
        return f"set {self._field} to {self.value}"


class Add(ActionExpression):
    """Add expression."""

    op = "add"

    def apply(self, i_dict: Dotty) -> bool:
        """Evaluate action."""
        val = i_dict.get(self.field, [])
        if isinstance(self.value, list):
            val.extend(self.value)
        else:
            val.append(self.value)
        i_dict[self.field] = val
        return True

    def __repr__(self):
        """Implement `repr()`."""
        return f"add {self.value} to {self._field}"
