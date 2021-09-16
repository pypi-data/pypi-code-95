from abc import ABC
from dataclasses import dataclass, field
from typing import Iterable, Optional, TextIO

from iolanta.models import LDContext, Quad, ContextAliases, LDDocument
from rdflib import URIRef
from urlpath import URL


@dataclass(frozen=True)
class Parser(ABC):
    """
    Parser reads data from a file-like object and interprets them.

    For interpretation, it is also supplied with a context.
    """

    def as_jsonld_document(self, raw_data: TextIO) -> LDDocument:
        """Generate a JSON-LD document."""
        raise NotImplementedError()
