from enum import Enum
from logging import config as logging_config
from types import MappingProxyType
from typing import Any, Dict, List, NamedTuple, Optional, Union

import rdflib
from rdflib import Graph, term
from typing_extensions import Protocol

OCTA = rdflib.Namespace('https://octadocs.io/')
IOLANTA = rdflib.Namespace('https://iolanta.tech/')
LOCAL = rdflib.Namespace('local:')


# To prevent WPS401 Found mutable module constant
DEFAULT_NAMESPACES = MappingProxyType({
    'octa': OCTA,
    'iolanta': IOLANTA,
    '': LOCAL,

    'rdf': rdflib.RDF,
    'rdfs': rdflib.RDFS,
    'xsd': rdflib.XSD,
    'schema': rdflib.SDO,
    'sh': rdflib.SH,
    'skos': rdflib.SKOS,
    'owl': rdflib.OWL,
    'dc': rdflib.DC,
    'dcat': rdflib.DCAT,
    'dcterms': rdflib.DCTERMS,
    'foaf': rdflib.FOAF,
})


DEFAULT_CONTEXT = MappingProxyType({
    '@vocab': LOCAL,
    '@base': LOCAL,

    'label': 'rdfs:label',
    'comment': 'rdfs:comment',
    'rdfs:isDefinedBy': {
        '@type': '@id',
    },
    'rdfs:subClassOf': {
        '@type': '@id',
    },
    'octa:subjectOf': {
        '@type': '@id',
    },

    'title': 'octa:title',
    'position': 'octa:position',

    # The default namespaces list should be included in context
    # We have to convert URLs to strings though - to make them serializable.
    **{
        namespace_name: str(namespace_url)
        for namespace_name, namespace_url
        in DEFAULT_NAMESPACES.items()
        if namespace_name
    },
})


class Triple(NamedTuple):
    """RDF triple."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]  # noqa: WPS125

    def as_quad(self, graph: rdflib.URIRef) -> 'Quad':
        """Add graph to this triple and hence get a quad."""
        return Quad(self.subject, self.predicate, self.object, graph)


class Quad(NamedTuple):
    """Triple assigned to a named graph."""

    subject: rdflib.URIRef
    predicate: rdflib.URIRef
    object: Union[rdflib.URIRef, rdflib.Literal]  # noqa: WPS125
    graph: rdflib.URIRef


# Should be Dict[str, 'Context'] but mypy crashes on a recursive type.
Context = Optional[   # type: ignore
    Union[str, int, float, Dict[str, Any]]
]


logging_config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})
SelectRow = Dict[str, term.Node]


class SelectResult(List[SelectRow]):
    """SPARQL SELECT query result."""

    @property
    def first(self) -> Optional[SelectRow]:
        """Return first element of the list."""
        return self[0] if self else None


QueryResult = Union[
    SelectResult,   # SELECT
    Graph,          # CONSTRUCT
    bool,           # ASK
]


class Query(Protocol):
    """Query protocol."""

    def __call__(
        self,
        query_text: str,
        instance: rdflib.ConjunctiveGraph,
        **kwargs: str,
    ) -> QueryResult:
        """Query prototype."""


class QueryResultsFormat(str, Enum):
    """Format to print query results in CLI."""

    PRETTY = 'pretty'
    CSV = 'csv'
    JSON = 'json'
