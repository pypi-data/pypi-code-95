from typing import Any, Dict, NamedTuple, Union

from rdflib import Literal, URIRef

# JSON-LD context

LDContext = Dict[str, Any]  # type: ignore
LDDocument = Dict[str, Any]  # type: ignore


# Named context URLs
ContextAliases = Dict[str, str]


class Triple(NamedTuple):
    """RDF triple."""

    subject: URIRef
    predicate: URIRef
    object: Union[URIRef, Literal]  # noqa: WPS125

    def as_quad(self, graph: URIRef) -> 'Quad':
        """Add graph to this triple and hence get a quad."""
        return Quad(
            subject=self.subject,
            predicate=self.predicate,
            object=self.object,
            graph=graph,
        )


class Quad(NamedTuple):
    """Triple assigned to a named graph."""

    subject: URIRef
    predicate: URIRef
    object: Union[URIRef, Literal]  # noqa: WPS125
    graph: URIRef

    def as_triple(self):
        """Convert this to triple."""
        return Triple(self.subject, self.predicate, self.object)

    def __repr__(self):
        return (
            f'(<{self.subject}> <{self.predicate}> <{self.object}> @ '
            f'{self.graph})'
        )
