"""Convert ParlaClarin XML protocol to other text format using Jinja."""
import os
import textwrap
from typing import Union

from click import echo
from jinja2 import Environment, PackageLoader, Template, Undefined, select_autoescape

from . import entities as model
from .dehyphenation.swe_dehyphen import get_dehyphenator
from .tokenize import tokenize
from .utility import strip_paths


def dedent(text: str) -> str:
    """Remove any white-space indentation from `text`."""
    if isinstance(text, Undefined):
        raise TypeError("dedent: jinja2.Undefined value string encountered")
    return textwrap.dedent(text) if text is not None else ""


def dehyphen(text: str) -> str:
    """Remove hyphens from `text`."""
    dehyphenated_text = get_dehyphenator().dehyphenator.dehyphen_text(text)
    return dehyphenated_text


def pretokenize(text: str) -> str:
    """Tokenize `text`, then join resulting tokens."""
    return ' '.join(tokenize(text))


jinja_env = Environment(
    loader=PackageLoader('resources', 'templates'),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True,
)
jinja_env.filters['dedent'] = dedent
jinja_env.filters['dehyphen'] = dehyphen


class ProtocolConverter:
    """Transform ParlaClarin XML to template-based format."""

    def __init__(self, template: Union[str, Template]):
        """[summary]

        Args:
            template (Union[str, Template]): Jinja template.
        """
        global jinja_env

        if not template.endswith(".jinja"):
            template += ".jinja"

        if isinstance(template, str):
            template = jinja_env.get_template(template)

        self.template: Template = template

    def convert(self, protocol: model.Protocol, filename: str) -> str:
        """Transform `protocol` and return resulting text."""
        text: str = self.template.render(protocol=protocol, filename=filename)
        return text


def convert_protocol(
    input_filename: str = None,
    output_filename: str = None,
    template_name: str = None,
):
    """Convert protocol in `input_filename' using template `template_name`. Store result in `output_filename`.

    Args:
        input_filename (str, optional): Source file. Defaults to None.
        output_filename (str, optional): Target file. Defaults to None.
        template_name (str, optional): Template name (found in resource-folder). Defaults to None.
    """
    protocol: model.Protocol = model.Protocol.from_file(input_filename)
    content: str = ""

    if protocol.has_speech_text():
        converter: ProtocolConverter = ProtocolConverter(template_name)
        content: str = converter.convert(protocol, strip_paths(input_filename))

    if output_filename is not None:
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        with open(output_filename, "w", encoding="utf-8") as fp:
            fp.write(content)
    else:
        echo(content, nl=False, err=False)
