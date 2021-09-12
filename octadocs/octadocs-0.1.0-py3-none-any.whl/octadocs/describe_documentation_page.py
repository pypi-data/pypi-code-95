from pathlib import Path
from typing import Iterator

from octadocs.types import LOCAL as local
from octadocs.types import OCTA as octa
from octadocs.types import Triple
from rdflib import RDF as rdf
from rdflib import Literal, URIRef


def describe_documentation_page(
    iri: URIRef,
    path: Path,
    docs_dir: Path,
) -> Iterator[Triple]:
    """Describe the file properties and hierarchy for the given page."""
    yield Triple(iri, octa.fileName, Literal(path.name))

    try:
        relative_path = path.relative_to(docs_dir)
    except ValueError:
        return

    try:
        breadcrumbs = list(relative_path.parents)[:-1]
    except ValueError:
        return

    children = [relative_path, *breadcrumbs]
    parents = [*children[1:], None]

    child_per_parent = zip(children, parents)

    for child, parent in child_per_parent:
        child_iri = local.term(str(child or ''))
        parent_iri = local.term(str(parent or ''))

        yield Triple(parent_iri, rdf.type, octa.Directory)
        yield Triple(child_iri, octa.isChildOf, parent_iri)

        if parent:
            yield Triple(parent_iri, octa.fileName, Literal(parent.name))

