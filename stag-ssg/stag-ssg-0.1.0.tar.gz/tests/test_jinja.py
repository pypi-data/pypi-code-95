import os
import pytest

from stag.utils import chdir
from stag.plugins.jinja import JinjaConfig, render

from testutils import add_md_file, contents


@pytest.fixture(autouse=True)
def jinja_config(config):
    config.plugins.theme = JinjaConfig()
    config.plugins.theme.name = "theme"
    return config


@pytest.fixture(autouse=True)
def default_templates(jinja_config, tmp_path):
    templates_dir = tmp_path / jinja_config.plugins.theme.name
    templates_dir.mkdir()

    html_templ = templates_dir / f"{jinja_config.plugins.theme.default_type}.html"
    html_content = "<html><body>{{ content }}</body></html>"
    html_templ.write_text(html_content)


def test_basic_gen(site, tmp_path):
    mdfile = add_md_file(site, "Content", parse=True)
    render_exp = f"<html><body>{mdfile.output.content}</body></html>"

    with chdir(tmp_path):
        render(mdfile, site)
        out = os.path.join(
            tmp_path, site.config.output, mdfile.url.strip("/"), "index.html"
        )
        assert contents(out) == render_exp
