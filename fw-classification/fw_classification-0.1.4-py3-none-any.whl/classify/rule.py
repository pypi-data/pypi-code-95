"""Implementation of Rule, and Match/Action sections."""
import enum
import typing as t

from dotty_dict import Dotty  # type: ignore

from .expressions import BinaryExpression, Expression
from .utils import MatchError, ProfileError, RuleError


class MatchType(enum.Enum):  # pragma: no cover
    """Enum for matching Any (OR) or All (AND)."""

    # pylint: disable=invalid-name

    Any = "any"
    All = "all"


class Match:
    """Match section of a rule."""

    def __init__(
        self,
        exprs: t.List[Expression],
        match_type: MatchType = MatchType.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        """Inialize a Match section.

        Args:
            exprs (t.List[Expression]): List of expressions specifying the match.
            match_type (MatchType, optional): Match type. Defaults to
                ``MatchType.Any``.
            variables (t.Optional[t.Dict[str, str]]): Alias dictionary. Optional,
                defaults to None
        """
        self.exprs = exprs
        self.match_type: MatchType = match_type
        self.variables = variables

    @property
    def variables(self) -> t.Optional[t.Dict[str, str]]:  # pragma: no cover
        """Get variables."""
        return self._variables

    @variables.setter
    def variables(self, variables: t.Optional[t.Dict[str, str]]) -> None:
        """Set variables."""
        # Update variables on expressions
        self._variables = variables
        for expr in self.exprs:
            expr.variables = variables

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate a match section against an i_dict.

        Args:
            i_dict (Dotty): Input dictionary.

        Raises:
            NotImplementedError: If an unknown match_type is specified

        Returns:
            bool: Result of evaluation.
        """
        if self.match_type == MatchType.Any:
            for expr in self.exprs:
                out = expr.evaluate(i_dict)
                if out:
                    return True
            return False
        if self.match_type == MatchType.All:
            for expr in self.exprs:
                out = expr.evaluate(i_dict)
                if not out:
                    return False
            return True
        # Shouldn't be possible to get here.
        raise ValueError(f"Unknown match type: {self.match_type}")  # pragma: no cover

    def __repr__(self) -> str:
        """Implment `repr(self)`."""
        out = f"Match if {self.match_type.value.capitalize()} are True: \n"
        for expr in self.exprs:
            out += f"\t- {repr(expr)}\n"
        return out

    @classmethod
    def from_list(
        cls,
        exprs: t.List,
        match_type: MatchType = MatchType.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
    ) -> t.Tuple[t.Optional["Match"], t.List[ProfileError]]:
        """Classmethod to initialize Match from a list.

        Args:
            exprs (t.List): List of dictionaries in the format of
                `fw_classification.base.Expression.from_dict`
            match_type (MatchType, optional): Match type. Defaults to
                ``MatchType.Any``.
            variables (t.Optional[t.Dict[str, str]], optional): Alias dictionary.
                Defaults to None.

        Returns:
            Tuple:
              - (Match or None): Instantiated Match object
              - (List[ProfileError]): Errors if any.
        """
        errors: t.List[ProfileError] = []
        expr_list: t.List[Expression] = []
        for expr in exprs:
            errs: t.List[ProfileError] = []
            expr_obj, errs = Expression.from_dict(expr)
            if errs:
                errors.extend([e.add_component("match") for e in errs])
                continue
            expr_list.append(expr_obj)  # type: ignore
        if not expr_list:
            if not errors:
                # Only add another error if there isn't one already
                errors.append(MatchError("Need at least one expression in match."))
            return None, errors
        m = cls(expr_list, match_type=match_type, variables=variables)  # type: ignore
        return m, errors

    def to_list(self) -> t.List[t.Dict]:
        """Convert self to a list of expression dicts."""
        return [expr.to_dict() for expr in self.exprs]


class Action:
    """Action section of a rule."""

    def __init__(
        self,
        exprs: t.List[BinaryExpression],
        variables: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        """Instantiate an Action object.

        Args:
            exprs (t.List[BinaryExpression]): List of expressions to apply.
            variables (t.Optional[t.Dict[str, str]]): Alias dictionary. Optional,
                defaults to None
        """
        self.exprs = exprs
        self.variables = variables

    @property
    def variables(self) -> t.Optional[t.Dict[str, str]]:  # pragma: no cover
        """Get variables."""
        return self._variables

    @variables.setter
    def variables(self, variables: t.Optional[t.Dict[str, str]]) -> None:
        """Set variables."""
        # Update variables on expressions
        self._variables = variables
        for expr in self.exprs:
            expr.variables = variables

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate a match section against an i_dict.

        Args:
            i_dict (Dotty): Input dictionary.

        Returns:
            bool: Result of evaluation.
        """
        for expr in self.exprs:
            out = expr.evaluate(i_dict)
            if not out:  # pragma: no cover
                # TODO: Add in test for this  # pylint: disable=fixme
                return False
        return True

    def __repr__(self) -> str:
        """Implement `repr(self)`."""
        out = "Do the following: \n"
        for expr in self.exprs:
            out += f"\t- {repr(expr)}\n"
        return out

    @classmethod
    def from_list(
        cls, exprs: t.List, variables: t.Optional[t.Dict[str, str]] = None
    ) -> t.Tuple[t.Optional["Action"], t.List[ProfileError]]:
        """Classmethod to initialize Action from a list.

        Args:
            exprs (t.List): List of dictionaries in the format of
                `fw_classification.base.Expression.from_dict`
            variables (t.Optional[t.Dict[str, str]], optional): Alias dictionary.
                Defaults to None.

        Returns:
            Tuple:
              - (Action or None): Instantiated Action object
              - (List[ProfileError]): Errors if any.
        """
        errors: t.List[ProfileError] = []
        expr_list = []
        for expr in exprs:
            errs: t.List[ProfileError] = []
            expr_obj, errs = Expression.from_dict(expr)
            if errs:
                errors.extend([e.add_component("action") for e in errs])
                continue
            expr_list.append(expr_obj)
        if not expr_list:
            return None, errors
        a = cls(expr_list, variables=variables)  # type: ignore
        return a, errors

    def to_list(self) -> t.List[t.Dict]:
        """Convert self to a list of expression dicts."""
        return [expr.to_dict() for expr in self.exprs]


class Rule:
    """Rule implementation."""

    def __init__(
        self,
        match: Match,
        action: t.Optional[Action],
        match_type: MatchType = MatchType.Any,
        variables: t.Optional[t.Dict[str, str]] = None,
    ) -> None:
        """Insantiate a rule.

        Args:
            match (Match): Match object.
            action (Action): Action object.
            match_type (MatchType, optional): MatchType. Default `MatchType.Any`.
            variables (t.Optional[t.Dict[str, str]]): Alias dictionary. Optional,
                defaults to None

        """
        self.match_type: MatchType = match_type
        # Update match type on Match object
        self.match = match
        self.match.match_type = self.match_type
        self.action = action
        self.variables = variables

    @property
    def variables(self) -> t.Optional[t.Dict[str, str]]:
        """Get variables."""
        return self._variables

    @variables.setter
    def variables(self, variables: t.Optional[t.Dict[str, str]]) -> None:
        """Set variables."""
        # Update variables on Match and Action object
        self._variables = variables
        self.match.variables = self.variables
        if self.action:
            self.action.variables = self.variables

    def evaluate(self, i_dict: Dotty) -> bool:
        """Evaluate rule."""
        matches = self.match.evaluate(i_dict)
        if matches:
            if self.action:
                applied = self.action.evaluate(i_dict)
                return applied
            return True
        return False

    def __repr__(self) -> str:
        """Implement `repr(self)`."""
        return repr(self.match) + "\n" + repr(self.action)

    @classmethod
    def from_dict(
        cls, rule: t.Dict, variables: t.Optional[t.Dict[str, str]] = None
    ) -> t.Tuple[t.Optional["Rule"], t.List[ProfileError]]:
        """Instantiate a Rule from a dictionary.

        Args:
            rule (t.Dict): [description]
            variables (t.Optional[t.Dict[str, str]], optional): Alias dictionary.
                Defaults to None.

        Returns:
            Tuple:
              - (Rule or None): Instantiated rule
              - (List[ProfileError): List of errors if any.
        """
        errors: t.List[ProfileError] = []
        rule_obj = None
        match, m_errs = Match.from_list(rule.get("match", []), variables=variables)
        errors.extend([e.add_component("rule") for e in m_errs])
        action, a_errs = Action.from_list(rule.get("action", []), variables=variables)
        errors.extend([e.add_component("rule") for e in a_errs])
        raw_match_type = rule.get("match_type")
        match_type = MatchType.Any
        # Only try to parse if match_type was set
        if raw_match_type:
            if raw_match_type == MatchType.All.value:
                match_type = MatchType.All
            elif raw_match_type == MatchType.Any.value:
                pass
            else:
                errors.append(RuleError(f"Unknown match_type {raw_match_type}"))
        if not errors:
            rule_obj = cls(
                match,  # type: ignore
                action,
                match_type=match_type,
                variables=variables,
            )
        return rule_obj, errors

    def to_dict(self) -> t.Dict:
        """Dump rule as a dictionary."""
        return {
            "match_type": self.match_type.value,
            "match": self.match.to_list(),
            "action": self.action.to_list() if self.action else {},
        }
