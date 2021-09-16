from dominate.tags import a
from more_itertools import first

from iolanta.facets.errors import PageNotFound
from octadocs.octiron import Octiron
from rdflib.term import Node, Literal


def default(octiron: Octiron, iri: Node) -> str:
    """Default facet to draw a link to something in HTML environment."""
    if isinstance(iri, Literal):
        return str(iri.value)

    descriptions = octiron.query(
        '''
        SELECT * WHERE {
            ?page rdfs:label ?label .

            OPTIONAL {
                ?page octa:symbol ?symbol .
            }

            OPTIONAL {
                ?page octa:url ?url .
            }

            OPTIONAL {
                ?page a octa:Page .
                BIND(true AS ?is_page)
            }
        } ORDER BY ?label LIMIT 1
        ''',
        page=iri,
    )
    location = first(descriptions, None)

    if not location:
        raise PageNotFound(iri=iri)

    label = location['label']
    symbol = location.get('symbol')

    if url := location.get('url'):
        symbol = symbol or (
            '📃' if location.get('is_page') else '🔗'
        )

        return a(
            f'{symbol} ',
            label,
            href=url,
        )

    if symbol:
        return f'{symbol} {label}'

    return label
