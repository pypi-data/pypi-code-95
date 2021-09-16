from typing import TextIO

import yaml

from iolanta.models import LDDocument
from iolanta.parsers.base import Parser
from octadocs.octiron.yaml_extensions import convert_dollar_signs

try:  # noqa
    from yaml import CSafeLoader as SafeLoader  # noqa
except ImportError:
    from yaml import SafeLoader  # type: ignore   # noqa


class YAML(Parser):
    """Load YAML data."""

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Read YAML content and adapt it to JSON-LD format."""
        document = yaml.load(raw_data, Loader=SafeLoader)
        return convert_dollar_signs(document)
