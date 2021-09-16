from abc import ABC
from dataclasses import dataclass, field
from typing import Iterable, Optional, TextIO, Type

from urlpath import URL

from iolanta.namespaces import PYTHON
from rdflib import URIRef

from iolanta.models import LDContext, Quad, ContextAliases, LDDocument
from iolanta.parsers.base import Parser
from iolanta.parsers.yaml import YAML


@dataclass(frozen=True)
class Loader(ABC):
    """
    Base class for loaders.

    Loader receives a URL (or a path) to certain location. It is responsible for
    reading data from that location and returning it as a stream of RDF quads.

    Usually, depending on the data format, Loader leverages Parsers for that
    purpose.
    """

    @classmethod
    def loader_class_iri(cls) -> URIRef:
        """Import path to the loader class."""
        return PYTHON.term(f'{cls.__module__}.{cls.__qualname__}')

    def choose_parser_class(self, url: URL) -> Type[Parser]:
        """Find which parser class to use for this URL."""
        return YAML

    def as_jsonld_document(
        self,
        url: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """Represent a file as a JSON-LD document."""
        raise NotImplementedError()

    def as_file(self, url: URL) -> TextIO:
        """Construct a file-like object."""
        raise NotImplementedError()

    def as_quad_stream(
        self,
        url: str,
        iri: Optional[URIRef],
        context: LDContext,
    ) -> Iterable[Quad]:
        """Convert data into a stream of RDF quads."""
        raise NotImplementedError()

    def __call__(self, url: str):
        raise NotImplementedError('This is for compatibility with PYLD.')
