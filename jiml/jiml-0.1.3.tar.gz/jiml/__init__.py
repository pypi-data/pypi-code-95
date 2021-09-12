import json
import pathlib

import jinja2
import yaml
from jinja_vanish import DynAutoEscapeEnvironment, markup_escape_func


__all__ = (
    'qstr', 'str', 'json_dumps',
    'FILTERS',
    'config',
    'JimlTemplate', 'JimlEnvironment',
    'load_template', 'render', 'convert',
)


# TODO: add exceptions


def yaml_escape(obj):
    if isinstance(obj, jinja2.Undefined):
        if isinstance(obj, jinja2.StrictUndefined):
            raise jinja2.exceptions.UndefinedError(f"Can't serialize StrictUndefined var '{obj._undefined_name}'")
        return ''

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


class JimlTemplate(jinja2.Template):
    def convert(self, *args, **kwargs):
        return yaml.safe_load(self.render(*args, **kwargs))

    __call__ = convert


class JimlEnvironment(DynAutoEscapeEnvironment):
    template_class = JimlTemplate

    def __init__(self, *args, autoescape=False, escape_func=None, **kwargs):
        if autoescape and escape_func is None:
            escape_func = markup_escape_func(yaml_escape)
        super().__init__(*args, autoescape=autoescape, escape_func=escape_func, **kwargs)
        self.filters.update(JIML_FILTERS)


_env = None


class EnvOptions:
    def __init__(self):
        self.values = {}

    def update(self, values):
        global _env

        self.values.update(values)
        _env = JimlEnvironment(**self.values)


config = EnvOptions()
config.update({
    'autoescape': True,
    'undefined': jinja2.StrictUndefined,
})
assert _env is not None


def load_template(template=None, path=None, env=None):
    if template is None:
        template = pathlib.Path(path).read_text()
    env = env or _env
    return env.from_string(template)


def render(template, context, env=None):
    return load_template(template, env=env).render(context)


def convert(template, context, env=None):
    return load_template(template, env=env).convert(context)
