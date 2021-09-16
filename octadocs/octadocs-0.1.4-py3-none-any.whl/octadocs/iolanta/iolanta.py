"""
Iolanta facet management.

This module contains a few functions which later will be refactored into
Iolanta - the generic metaverse/cyberspace browser.
"""
import operator
import pydoc
from typing import Optional, Callable, Union

from more_itertools import first
from octadocs.iolanta.errors import FacetNotCallable, FacetNotFound
from rdflib.term import Node, URIRef
from urlpath import URL

from octadocs.octiron import Octiron


HTML = URIRef('https://html.spec.whatwg.org/')


def find_default_facet_iri_for_environment(octiron: Octiron, environment: URIRef):
    rows = octiron.query(
        '''
        SELECT * WHERE {
            ?environment iolanta:hasDefaultFacet ?facet .
        }
        ''',
        environment=environment,
    )

    facets = map(operator.itemgetter('facet'), rows)

    return first(facets, None)


def find_facet_iri(
    octiron: Octiron,
    environment: URIRef,
    node: Node,
) -> Optional[URIRef]:
    if not isinstance(node, URIRef):
        node = URIRef(node)

    rows = octiron.query(
        '''
        SELECT ?facet WHERE {
            ?node iolanta:facet ?facet .
            ?facet iolanta:supports ?environment .
        }
        ''',
        node=node,
        environment=environment,
    )

    facets = map(operator.itemgetter('facet'), rows)

    if facet := first(facets, None):
        return facet

    facet = find_default_facet_iri_for_environment(
        octiron=octiron,
        environment=environment,
    )

    if facet is None:
        raise FacetNotFound(
            node=node,
            environment=environment,
        )

    return facet


def resolve_facet(iri: URIRef) -> Callable[[Octiron, Node], str]:
    url = URL(str(iri))

    if url.scheme != 'python':
        raise Exception(
            'Octadocs only supports facets which are importable Python '
            'callables. The URLs of such facets must start with `python://`, '
            'which {url} does not comply to.'.format(
                url=url,
            )
        )

    import_path = url.hostname
    facet = pydoc.locate(import_path)

    if not callable(facet):
        raise FacetNotCallable(
            path=import_path,
            facet=facet,
        )

    return facet


def render(
    node: Union[str, Node],
    octiron: Octiron,
    environment: URIRef = HTML,
) -> str:
    """Find an Iolanta facet for a node and render it."""
    facet_iri = find_facet_iri(
        octiron=octiron,
        environment=environment,
        node=node,
    )

    facet = resolve_facet(iri=facet_iri)

    return facet(
        octiron=octiron,
        iri=node,
    )
