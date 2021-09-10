import json

import jinja2
import yaml


__all__ = (
    'qstr', 'str', 'json_dumps', 'FILTERS', 'Environment', 'convert',
)


def qstr(inp):
    if inp is None:
        inp = ''
    return json.dumps(str(inp))


def str_(inp):
    return qstr(inp)[1:-1]


def json_dumps(inp):
    return json.dumps(inp, ensure_ascii=False)


JAML_FILTERS = {
    'qstr': qstr,
    'str': str_,
    'json.dumps': json_dumps,
}


class Environment(jinja2.Environment):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters.update(JAML_FILTERS)


_env = Environment()


def render(template, context):
    return _env.from_string(template).render(context)


def convert(template, context):
    return yaml.safe_load(render(template, context))
