import pytest

from stag.utils import chdir
from stag.plugins.macros import MacrosConfig, resolve_macros
from stag.plugins.jinja import JinjaConfig

from testutils import add_md_file, contents


@pytest.fixture(autouse=True)
def macros_config(config):
    config.plugins.macros = MacrosConfig()
    config.plugins.macros.path = "macros"

    config.plugins.theme = JinjaConfig()
    config.plugins.theme.name = "theme"
    return config


@pytest.fixture(autouse=True)
def default_macros(macros_config, tmp_path):
    macros_dir = tmp_path / macros_config.plugins.macros.path
    macros_dir.mkdir()

    macro_templ = macros_dir / "macros.html"
    macro_content = "{%macro bold(name)%}<b>{{name}}</b>{% endmacro %}"
    macro_templ.write_text(macro_content)


def test_macros(site, tmp_path):
    content = '{%from "macros.html" import bold%}**foo** {{ bold("bar") }}'
    render_exp = f"**foo** <b>bar</b>"

    mdfile = add_md_file(site, content)

    with chdir(tmp_path):
        resolve_macros(mdfile, site)
        assert mdfile.input.content == render_exp
