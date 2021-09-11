import json

import jinja2
import yaml
from jinja_vanish import DynAutoEscapeEnvironment, markup_escape_func


__all__ = (
    'qstr', 'str', 'json_dumps', 'FILTERS', 'Environment', 'convert',
)


def yaml_escape(obj):
    res = yaml.dump(
        obj,
        width=float("inf"),
        default_flow_style=True,
        default_style='"',
    ).strip('\n')
    if '\n' in res:
        raise ValueError('escaped value contains newline symbol for object {}'.format(obj))
    return res


def _qstr(inp):
    if inp is None:
        inp = ''
    return json.dumps(str(inp))


def qstr(inp):
    return jinja2.Markup(_qstr(inp))


def str_(inp):
    return jinja2.Markup(_qstr(inp)[1:-1])


def json_dumps(inp):
    return jinja2.Markup(json.dumps(inp, ensure_ascii=False))


JIML_FILTERS = {
    'qstr': qstr,
    'str': str_,
    'json.dumps': json_dumps,
    'yaml.dumps': yaml_escape,
    'e': yaml_escape,
    'escape': yaml_escape,
}


class Environment(DynAutoEscapeEnvironment):
    def __init__(self, *args, autoescape=False, escape_func=None, **kwargs):
        if autoescape and escape_func is None:
            escape_func = markup_escape_func(yaml_escape)
        super().__init__(*args, autoescape=autoescape, escape_func=escape_func, **kwargs)
        self.filters.update(JIML_FILTERS)


_autoescape_env = Environment(autoescape=True)
_env = Environment()


def render(template, context, autoescape=True):
    env = _autoescape_env if autoescape else _env
    return env.from_string(template).render(context)


def convert(template, context, autoescape=True):
    return yaml.safe_load(render(template, context, autoescape=autoescape))
