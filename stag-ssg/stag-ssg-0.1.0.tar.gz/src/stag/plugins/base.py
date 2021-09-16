import logging
from functools import wraps as _wraps
from functools import partial as _partial

from typing import Optional as _Optional
from typing import List as _List
from collections.abc import Callable as _Callable
from collections import namedtuple

import attr

from stag.ecs import Page, Site


log = logging.getLogger(__name__)


def run_always(*a, **kw):
    """Helper function which can be used when registering plugins to mark that
    they should be run for all files."""
    return True


_Cond = _Callable[[Page], bool]
_Plugin = _Callable
_PlugConfig = _Optional[object]


@attr.s(auto_attribs=True)
class PlugData:
    name: str
    plugin: _Plugin
    condition: _Cond
    config: _PlugConfig


_READERS = {}
_GENERATORS = {}
_WRITERS = {}


def _register_impl(out: list, name: str, *a) -> None:
    if name in out:
        raise KeyError(f"name conflict: {name}")
    out[name] = PlugData(name, *a)


def _register(
    where: dict, name: str, cond: _Cond = run_always, config: _PlugConfig = None
):
    def decor(fn):
        _register_impl(where, name, fn, cond, config)

        @_wraps(fn)
        def wrapper(*a, **kw):
            return fn(*a, **kw)

        return wrapper

    return decor


def _get_enabled_in_order(plugins, order=None):
    if order is None:
        return list(plugins.values())

    ret = []
    for name in order:
        try:
            ret.append(plugins[name])
        except KeyError:
            log.error(f"Plugin not found: {name}")
            continue
    return ret


reader = _partial(_register, _READERS)
generator = _partial(_register, _GENERATORS)
writer = _partial(_register, _WRITERS)

readers = _partial(_get_enabled_in_order, _READERS)
generators = _partial(_get_enabled_in_order, _GENERATORS)
writers = _partial(_get_enabled_in_order, _WRITERS)
