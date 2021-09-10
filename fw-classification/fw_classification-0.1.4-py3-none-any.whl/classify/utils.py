"""Utilities module."""
import logging
import pprint
import textwrap
import typing as t

__all__ = [
    "ProfileError",
    "BlockError",
    "MatchError",
    "RuleError",
    "ExpressionError",
    "configure_logging",
]


def configure_logging(name: str) -> logging.Logger:
    """Configure info or debug level logging."""
    root = logging.getLogger()
    # Use full name if debug, otherwise shorten to module.
    if root.level < logging.INFO:
        return logging.getLogger(name)
    return logging.getLogger(name.split(".")[0])


class ProfileError:
    """Classification profile error."""

    component = "profile"

    def __init__(
        self,
        c_name: t.Optional[str],
        msg: str,
        raw: t.Optional[t.Dict] = None,
    ) -> None:
        """Instantiate ProfileError."""
        self.c_name = c_name
        self.msg = msg
        self.raw = raw
        self.stack = [self.component + (f" ({c_name})" if c_name else "")]

    def add_component(self, component: str) -> "ProfileError":
        """Add component level to stack."""
        self.stack.append(component)
        return self

    def __repr__(self) -> str:
        """String representation."""
        err_str = f"{self.component} "
        err_str += f"({self.c_name})" if self.c_name else ""
        err_str += f": {self.msg}\n"
        if self.raw:
            err_str += textwrap.indent(f"Raw dict: {pprint.pformat(self.raw)}", "\t")
        if self.stack:
            stack = list(reversed(self.stack))
            err_str += "\n  Traceback:\n\t"
            err_str += "\n\t".join(stack)
        return err_str


class BlockError(ProfileError):
    """ProfileError with component set to "block"."""

    component = "block"


class MatchError(ProfileError):
    """ProfileError with component set to "match"."""

    component = "match"

    def __init__(self, msg: str, raw: t.Optional[t.Dict] = None) -> None:
        """Lock component name to None."""
        super().__init__(None, msg, raw)


class RuleError(ProfileError):
    """ProfileError with component set to "rule"."""

    component = "rule"

    def __init__(self, msg: str, raw: t.Optional[t.Dict] = None) -> None:
        """Lock component name to None."""
        super().__init__(None, msg, raw)


class ExpressionError(ProfileError):
    """ProfileError with component set to "expression"."""

    component = "expression"

    def __init__(self, msg: str, raw: t.Optional[t.Dict] = None) -> None:
        """Lock component name to None."""
        super().__init__(None, msg, raw)
