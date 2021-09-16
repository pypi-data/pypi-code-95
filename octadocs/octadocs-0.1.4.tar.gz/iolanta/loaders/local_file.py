from typing import TextIO, Optional, Iterable

from rdflib import URIRef
from urlpath import URL

from iolanta.conversions import url_to_path
from iolanta.loaders.base import Loader
from iolanta.models import LDDocument, LDContext, Quad


class LocalFile(Loader):
    """
    Retrieve Linked Data from a file on local disk.

    Requires URL with file:// scheme as input.
    """

    def as_quad_stream(
        self,
        url: str,
        iri: Optional[URIRef],
        context: LDContext,
    ) -> Iterable[Quad]:
        raise ValueError('!')

    def __call__(self, url: str):
        pass

    def as_file(self, url: URL) -> TextIO:
        """Construct a file-like object."""
        path = url_to_path(url)
        with path.open() as text_io:
            return text_io

    def as_jsonld_document(
        self,
        url: URL,
        iri: Optional[URIRef] = None,
    ) -> LDDocument:
        """As JSON-LD document."""
        parser_class = self.choose_parser_class(url)

        with url_to_path(url).open() as text_io:
            document = parser_class().as_jsonld_document(text_io)

        if iri is not None:
            document.setdefault('@id', str(iri))

        return document
