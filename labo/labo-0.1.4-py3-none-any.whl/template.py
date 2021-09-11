import os

import jinja2

std_env = jinja2.Environment(
    autoescape=False,
)

latex_jinja_env = jinja2.Environment(
    block_start_string="\BLOCK{",
    block_end_string="}",
    variable_start_string="\VAR{",
    variable_end_string="}",
    comment_start_string="\#{",
    comment_end_string="}",
    line_statement_prefix="%-",
    line_comment_prefix="%#",
    trim_blocks=True,
    autoescape=False,
)


def render_latex_template(path, name, variables):
    """Renders a Jinja2 LaTeX template."""
    latex_jinja_env.loader = jinja2.FileSystemLoader(path)
    template = latex_jinja_env.get_template(name)
    return template.render(**variables)


def render_makefile_template(path, name, variables):
    """Renders a Jinja2 Makefile template."""
    std_env.loader = jinja2.FileSystemLoader(path)
    template = std_env.get_template(name)
    return template.render(**variables)
