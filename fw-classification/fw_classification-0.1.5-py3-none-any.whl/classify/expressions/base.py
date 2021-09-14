"""Expression base classes."""
import abc
import re
import typing as t

from dotty_dict import Dotty  # type: ignore

from ..utils import ExpressionError, ProfileError


class Expression(abc.ABC):
    """Base class for expressions.

    Attributes:
        op (str): Key that each concrete subclass should set, used to match
            a particular operation key to the class that handles it.
        op_type (str): Type of operation, either Binary or Unary.
        variables (t.Optional[t.Dict[str, str]]): Dictionary representing
            variables associated with the expression.
    """

    op: str = ""
    op_type: str = ""
    variables: t.Optional[t.Dict[str, str]] = None

    @abc.abstractmethod
    def __init__(self, *args, **kwargs) -> None:  # pragma: no cover
        """Initialize expression."""

    @abc.abstractmethod
    def evaluate(self, i_dict: Dotty) -> bool:  # pragma: no cover
        """Evaluate expression."""
        raise NotImplementedError

    @abc.abstractmethod
    def __repr__(self):  # pragma: no cover
        """Implement `repr()`."""
        raise NotImplementedError

    @classmethod
    def from_dict(  # pylint: disable=too-many-locals
        cls, in_expr: t.Dict, variables: t.Optional[t.Dict[str, str]] = None
    ) -> t.Tuple[t.Optional["Expression"], t.List[ProfileError]]:
        """Return an instantiated  expression subclass from a dictionary.

        Args:
            in_expr (t.Dict): Expression dictionary.
            variables (t.Optional[t.Dict[str, str]], optional): Alias dictionary.
                Defaults to None.

        The dictionary should be of the form specified in either `UnaryExpression`,
        or `BinaryExpression`

        Returns:
            Tuple:
                - (Expression or None): Expression subclass with the proper op.
                - (ProfileError or None): Error if any.

        """
        from . import (  # pylint: disable=import-outside-toplevel,cyclic-import
            expression_map,
        )

        expr = in_expr.copy()
        e_errs: t.List[ProfileError] = []
        expr_obj: t.Optional["Expression"] = None
        keys = list(expr.keys())
        # Remove 'key' from search for op_key if present
        if "key" in expr:
            keys.remove("key")
        for op_key in keys:
            if op_key in expression_map:
                op_type, subcls = expression_map[op_key]
                if op_type == "binary":
                    if "key" not in expr:
                        e_errs.append(
                            ExpressionError(
                                "'key' must be in expression dict.", raw=in_expr
                            )
                        )
                        return None, e_errs
                    field = expr.pop("key")
                    value = expr.pop(op_key)
                    err = subcls.validate(field, value, variables=variables, **expr)
                    if err:
                        e_errs.append(ExpressionError("\n".join(err), raw=in_expr))
                        return None, e_errs
                    expr_obj = subcls(field, value, variables=variables, **expr)
                    return expr_obj, e_errs
                # Unary: recurse into grouping op
                sub_expr_objs: t.List[Expression] = []
                expr_list = expr.pop(op_key, [])
                if not isinstance(expr_list, list):
                    e_errs.append(
                        ExpressionError(  # type: ignore
                            f"Value of op '{op_key}' must be a list, found"
                            f": {expr_list}",
                            raw=in_expr,
                        )
                    )
                    continue
                for sub_expr in expr_list:
                    sub_expr_err: t.List[ProfileError] = []
                    (sub_expr_obj, sub_expr_err) = cls.from_dict(
                        sub_expr, variables=variables
                    )  # type: ignore
                    if sub_expr_err:
                        e_errs.extend(sub_expr_err)
                        continue
                    sub_expr_objs.append(sub_expr_obj)  # type: ignore
                err = subcls.validate(sub_expr_objs)
                if err:
                    e_errs.append(ExpressionError("\n".join(err), raw=in_expr))
                if e_errs:
                    return None, e_errs
                expr_obj = subcls(sub_expr_objs)
                return expr_obj, e_errs

        e_errs.append(
            ExpressionError(  # type: ignore
                f"Could not find implemented expressions for op keys '{keys}'",
                raw=in_expr,
            )
        )
        return None, e_errs

    @abc.abstractmethod
    def to_dict(self) -> t.Dict:  # pragma: no cover
        """Dump expression as a dictionary."""
        raise NotImplementedError


class UnaryExpression(Expression):  # pragma: no cover
    """Base class for unary expressions.

    The subclasses of this class are instantiated from
    a dictionary of the form:

    .. code-block::python
        {
            <operator>: [<val1>, <val2>, ...]
        }
    """

    op_type = "unary"

    def __init__(
        self,
        exprs: t.List[Expression],
        variables: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        """Initialize Expression.

        Args:
            exprs (t.List[Expression]): List of expressions.
            variables (t.Optional[t.Dict[str, str]], optional): Alias dictionary.
                Defaults to None.
        """
        super().__init__(exprs)
        self.exprs = exprs
        self.variables = variables
        for expr in self.exprs:
            expr.variables = variables

    @staticmethod
    def validate(  # pylint: disable=unused-argument
        exprs: t.List[Expression],
        variables: t.Optional[t.Dict[str, str]] = None,
        **kwargs,
    ) -> t.List[str]:
        """Validate a raw UnaryExpression before instantiating."""
        errs: t.List[str] = []
        # Trivial here since validate for BinaryExpression would
        #   have been called on each sub_expr, in Expression.from_dict.
        #   But still provide this so subclasses can override.
        return errs

    def __eq__(self, other: object) -> bool:  # pylint: disable=unidiomatic-typecheck
        """Implement `is`."""
        return isinstance(other, self.__class__) and set(self.exprs) == set(other.exprs)

    def __hash__(self) -> int:
        """Implement `hash()`."""
        return hash(type(self)) + hash(tuple(self.exprs))

    def to_dict(self) -> t.Dict:
        """Implement to_dict."""
        return {self.op: [expr.to_dict() for expr in self.exprs]}


class BinaryExpression(Expression):
    """Base class for binary expressions.

    The subclasses of this class are instantiated from
    a dictionary of the form:

    .. code-block:: python

        {
            'key': <field>
            <operator>: <value>
        }

    Each subclass has an attribute ``op`` that matches the
    ``<operator>`` key in the dictionary.

    """

    op_type = "binary"
    # Matches:
    #   - $fm
    #   - $fm.value
    variable_regex = re.compile(r"^\$(\w*)\.?(\w+)?$")

    def __init__(
        self,
        field: str,
        val: t.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
        **kwargs,
    ) -> None:
        """Initialize BinaryExpression.

        Args:
            field (str): Name of field following ``key``
            val (Any): Value for the operator
            variables (Optional[Dict[str, str]]): Variable dictionary. Optional,
                defaults to None
            kwargs: Custom config options handled by subclasses.
        """
        super().__init__(field, val)
        self._field = field
        self._value = val
        self.variables = variables
        self.config = kwargs

    def _inject_variables(self, val: t.Any) -> t.Any:
        if self.variables is None:
            self.variables = {}
        if match := self.variable_regex.match(val):
            variable, key = match.groups()
            sub: str = ""
            try:
                sub = self.variables[variable]
            except KeyError as e:
                raise ValueError(f"Variable {variable} not found.") from e
            return sub + ("." + key if key else "")
        return val

    @property
    def field(self) -> str:
        """Field property injecting variables."""
        return self._inject_variables(self._field)

    @property
    def value(self) -> t.Any:
        """Value property injecting variables."""
        return self._value

    @staticmethod
    def validate(  # pylint: disable=unused-argument
        field: str,
        val: t.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
        **kwargs,
    ) -> t.List[str]:
        """Validate a raw BinaryExpressoin before instantiating."""
        errs: t.List[str] = []
        if not isinstance(field, str):
            errs.append(f"Field must be a string, found {field}")
        if variables:
            for k, v in variables.items():
                if not isinstance(k, str):
                    errs.append(f"Variable key must be str, found {k}")
                if not isinstance(v, str):
                    errs.append(f"Variable value must be str, found {v}")
        return errs

    def get_value(self, i_dict: Dotty) -> t.Any:
        """Get value in input-dict if exists, replacing `None` with ""."""
        return i_dict.get(self.field, "") or ""

    def __eq__(self, other: object) -> bool:
        """Implement `is`."""
        return (
            isinstance(other, self.__class__)
            and self.field == other.field
            and self.value == other.value
        )

    def __hash__(self) -> int:
        """Implement `hash()`."""
        return hash(type(self)) + hash(self.field) + hash(self.value)

    def to_dict(self) -> t.Dict:
        """Implement to_dict."""
        return {"key": self._field, self.op: self.value}


class MatchExpression(BinaryExpression):
    """Base class to represent the :ref:`match` section of a rule."""

    @abc.abstractmethod
    def matches(self, i_dict: Dotty) -> bool:  # pragma: no cover
        """Evaluate `MatchExpression`."""
        raise NotImplementedError

    def evaluate(self, i_dict: Dotty) -> bool:
        """Wrap for `matches`."""
        return self.matches(i_dict)


class ActionExpression(BinaryExpression):
    """Base class to represent the :ref:`action` section of a rule."""

    @abc.abstractmethod
    def apply(self, i_dict: Dotty) -> bool:  # pragma: no cover
        """Evaluate `ActionExpression`."""
        raise NotImplementedError

    def evaluate(self, i_dict: Dotty) -> bool:
        """Wrap `apply`."""
        return self.apply(i_dict)
