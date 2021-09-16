from dataclasses import dataclass

from documented import DocumentedError
from rdflib import URIRef
from rdflib.term import Node


@dataclass
class FacetNotCallable(DocumentedError):
    """
    Python facet not callable.

      - Import path: {self.path}
      - Object imported: {self.facet}

    The imported Python object is not a callable and thus cannot be used as a
    facet.
    """

    path: str
    facet: object


@dataclass
class FacetNotFound(DocumentedError):
    """
    Facet not found.

    !!! error "No way to render the node you asked for"
        - **Node:** `{self.node}`
        - **Environment:** [{self.environment}]({self.environment})

        We could not find a facet to display this node 😟

        - Ensure the node exists in the graph;
        - Make sure it has an `iolanta:facet` declaration, and that the facet it
          is bound to declares that it `iolanta:supports` `{self.environment}`
          environment;
        - Or at least that mentioned environment via `iolanta:hasDefaultFacet`
          points to a facet that, by default, can be used to render nodes in it.
    """

    node: Node
    environment: URIRef
