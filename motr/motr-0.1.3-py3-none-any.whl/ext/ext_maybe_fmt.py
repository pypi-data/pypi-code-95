"""MOTR conditional formatting module."""

import typing

import attr
import blessed.formatters
import cement


def maybe_format(value: str, func: typing.Callable[[str], str]) -> str:
    if value:
        return func(value)
    return value


def maybe_header(value: str, header: str) -> str:
    return maybe_format(value, header.__add__)


@attr.dataclass(frozen=True)
class Color:
    app: cement.App

    def __call__(self, value: str, color: str) -> str:
        assert color in blessed.formatters.COLORS  # type: ignore
        return getattr(self.app.term, color)(value)


@attr.dataclass(frozen=True)
class MaybeColor:
    app: cement.App

    def __call__(self, value: str, color: str) -> str:
        # blessed messed up their type annotations
        assert color in blessed.formatters.COLORS  # type: ignore
        return maybe_format(value, getattr(self.app.term, color))


def register_filter(
    name: str, filter_func: typing.Callable
) -> typing.Callable:
    def register(app: cement.App) -> None:
        assert app.output
        assert app.output.Meta.label == "jinja2"
        app.output.templater.env.filters[name] = filter_func

    return register


COLOR_ARGS = {
    "auto": False,
    "always": True,
    "never": None,
}


def make_term(app: cement.App) -> None:
    assert app.pargs is not None
    color: bool
    # Get it together, blessed.
    color = COLOR_ARGS[app.pargs.color]  # type: ignore
    app.term = blessed.Terminal(force_styling=color)


def add_color_arg(app: cement.App) -> None:
    app.add_arg("--color", default="auto", choices=["auto", "always", "never"])


def load(app: cement.App) -> None:
    app.hook.register(
        "post_setup", register_filter("maybe_header", maybe_header)
    )
    app.hook.register(
        "post_setup",
        register_filter("maybe_color", MaybeColor(app)),
    )
    app.hook.register("post_setup", register_filter("color", Color(app)))
    app.hook.register("post_argument_parsing", make_term)
    app.hook.register("post_setup", add_color_arg)
