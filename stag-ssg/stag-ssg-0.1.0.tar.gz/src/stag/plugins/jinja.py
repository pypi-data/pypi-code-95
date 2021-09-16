import os
import logging
from functools import cache

import attr
from jinja2 import Template, Environment, FileSystemLoader, FunctionLoader, ChoiceLoader

from .base import writer
from ._jinja_functions import update_env

try:
    from stag._version import version
except ImportError:
    version = "unknown version"


log = logging.getLogger(__name__)


_DEFAULT_TEMPLATE = "{{ content }}"
_DEFAULT_HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="{{{{ site.config.get('lang', 'en') }}}}">
  <head>
    <meta name="generator" content="stag ({version})" />
    <meta charset="UTF-8">
    <title>{{{{ page.metadata.title }}}} - {{{{ site.config.title }}}}</title>
  </head>
  <body>
  {{{{ content }}}}
  </body>
</html>
"""


def load_default_template(name):
    log.error(f"Template not found: {name}. Using built-in basic template.")
    _, ext = os.path.splitext(name)
    template = _DEFAULT_HTML_TEMPLATE if ext == ".html" else _DEFAULT_TEMPLATE
    return template


@attr.s(auto_attribs=True)
class JinjaConfig:
    name: str = os.path.join("themes", "default")
    templates: dict = attr.ib(factory=dict)

    def __attrs_post_init__(self):
        default_templates = dict(page="page", list="list", taxonomy="taxonomy")
        default_templates.update(self.templates)
        self.templates = default_templates


def outputable(page):
    return page.output and page.metadata


@cache
def get_env(theme):
    env = Environment(
        loader=ChoiceLoader(
            [
                FileSystemLoader(theme),
                FunctionLoader(load_default_template),
            ]
        ),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    update_env(env)
    return env


def is_list(page):
    return bool(page.list)


def is_taxonomy(page):
    return bool(page.taxonomy)


def get_default_type(page, templates):
    if is_taxonomy(page):
        return templates["taxonomy"]
    if is_list(page):
        return templates["list"]
    return templates["page"]


def render_page(page, site, env):
    config = site.config
    myconfig = config.plugins.theme

    type_ = page.metadata.get("type")
    if not type_:
        type_ = get_default_type(page, myconfig.templates)

    template = env.get_template(f"{type_}.{page.output.type}")
    url = page.url.strip("/")
    filename = f"index.{page.output.type}"

    outpath = os.path.join(config.output, url, filename)
    outdir = os.path.dirname(outpath)

    if os.path.exists(outpath):
        log.error(f"page already exists, skipping: {outpath}")
        return

    os.makedirs(outdir, exist_ok=True)
    with open(outpath, "w") as fd:
        fd.write(template.render(content=page.output.content, site=site, page=page))


@writer("theme", cond=outputable, config=JinjaConfig())
def render(page, site):
    env = get_env(site.config.plugins.theme.name)
    return render_page(page, site, env)
