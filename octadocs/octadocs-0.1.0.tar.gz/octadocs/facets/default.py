from dataclasses import dataclass

from documented import DocumentedError
from dominate.tags import a
from more_itertools import first
from rdflib import URIRef

from octadocs.octiron import Octiron
from rdflib.term import Node, Literal


@dataclass
class PageNotFound(DocumentedError):
    """
    Page not found by IRI: `{self.iri}`.

    !!! error "Page not found by IRI: `{self.iri}`"
        Every page on your documentation site, just as any other entity described on
        it, has an IRI — a unique identifier similar to a URL. IRI can be generated
        in two alternative ways.

          1. If you wanted to use IRI generated automatically, then please confirm
             that in the `docs` directory there is a file under the following path:

             ```
             {self.possible_path}
             ```

          2. If you wanted to use IRI that you specified explicitly then confirm
             there is a Markdown file somewhere in `docs` directory which contains
             the following text in its header:

             ```markdown
             ---
             $id: {self.possible_id}
             ---
             ```
    """

    iri: URIRef

    @property
    def possible_path(self) -> str:
        """Guess on a possible path."""
        base_path = str(self.iri).replace('local:', '')
        return f'{base_path}.md'

    @property
    def possible_id(self) -> str:
        """Guess on a possible $id."""
        return str(self.iri).replace('local:', '')


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
