from functools import cache

from typing import Optional as _Optional

import attr
from jinja2 import Template, Environment, ChoiceLoader, FileSystemLoader
from jinja2.exceptions import TemplateSyntaxError, TemplateNotFound

from .base import generator


class MacroError(Exception):
    pass


def raise_macro_error(msg):
    raise MacroError(msg)


@attr.s(auto_attribs=True)
class MacrosConfig:
    path: _Optional[str] = None


def cond(page):
    return page.source and page.input and page.input.content


@cache
def get_env(macros_dir, theme_dir):
    loaders = [FileSystemLoader(dir) for dir in [macros_dir, theme_dir] if dir]
    env = Environment(
        loader=ChoiceLoader(loaders), trim_blocks=True, lstrip_blocks=True
    )
    env.globals["raise"] = raise_macro_error

    return env


@generator("macros", cond=cond, config=MacrosConfig())
def resolve_macros(page, site):
    config = site.config
    myconfig = config.plugins.macros

    env = get_env(myconfig.path, config.plugins.theme.name)
    env.globals["site"] = site
    env.globals["print"] = print

    try:
        template = env.from_string(page.input.content)
        page.input.content = template.render(page=page, site=site)
    except TemplateNotFound as e:
        raise MacroError(f"{page.source.relpath}: missing macro definitions file: {e}")
    except Exception as e:
        raise MacroError(f"{page.source.relpath}: {e}")
