from typing import Protocol

from octadocs.octiron import Octiron
from rdflib import URIRef
from rdflib.term import Node


class PythonFacet(Protocol):
    """Prototype of a Python facet function."""

    def __call__(
        self,
        octiron: Octiron,
        node: Node,
        environment: URIRef,
    ) -> str:
        ...
