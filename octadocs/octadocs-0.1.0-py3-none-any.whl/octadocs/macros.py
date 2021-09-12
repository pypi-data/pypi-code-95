from functools import partial
from typing import Any, Dict, Optional, Union

import rdflib
from mkdocs_macros.plugin import MacrosPlugin

from octadocs.conversions import iri_by_page, src_path_to_iri
from octadocs.environment import iri_to_url
from octadocs.iolanta import render, find_facet_iri
from octadocs.octiron import Octiron
from octadocs.query import query
from rdflib.plugins.sparql.processor import SPARQLResult

from octadocs.types import LOCAL, OCTA


def sparql(
    instance: rdflib.ConjunctiveGraph,
    query: str,
    **kwargs: str,
) -> SPARQLResult:
    bindings = {
        argument_name: argument_value
        for argument_name, argument_value in kwargs.items()
    }

    return instance.query(query, initBindings=bindings)


def _render_as_row(row: Dict[rdflib.Variable, Any]) -> str:  # type: ignore
    """Render row of a Markdown table."""
    formatted_row = ' | '.join(row.values())
    return f'| {formatted_row} |'


def table(query_result: SPARQLResult) -> str:
    """Render as a Markdown table."""
    headers = ' | '.join(str(cell) for cell in query_result.vars)

    rows = '\n'.join(
        _render_as_row(row)
        for row in query_result.bindings
    )

    separators = '| ' + (' --- |' * len(query_result.vars))  # noqa: WPS336

    return f'''
---
| {headers} |
{separators}
{rows}
'''


def url(
    resource: rdflib.URIRef,
    graph: rdflib.ConjunctiveGraph
) -> Optional[str]:
    """Convert a URIRef to a clickable URL."""
    bindings = graph.query(
        'SELECT ?url WHERE { ?resource octa:subjectOf/octa:url ?url . } ',
        initBindings={
            'resource': resource,
        }
    ).bindings

    if not bindings:
        return None

    return '/' + bindings[0][rdflib.Variable('url')].value


def label(
    resource: rdflib.URIRef,
    graph: rdflib.ConjunctiveGraph
) -> Optional[str]:
    """Convert a URIRef to a clickable URL."""
    bindings = graph.query(
        'SELECT ?label WHERE { ?resource rdfs:label ?label . } ',
        initBindings={
            'resource': resource,
        }
    ).bindings

    if not bindings:
        return None

    return bindings[0][rdflib.Variable('label')].value


def link(reference: Union[str, rdflib.URIRef], octiron: Octiron) -> str:
    """Render link to the object."""
    if isinstance(reference, str):
        if ':' in reference:
            reference = rdflib.URIRef(reference)
        else:
            reference = LOCAL.term(reference)

    return render(
        node=reference,
        octiron=octiron,
        environment=OCTA.link,
    )


def define_env(env: MacrosPlugin) -> MacrosPlugin:  # noqa: WPS213
    """Create mkdocs-macros Jinja environment."""
    env.filter(sparql)
    env.filter(table)

    octiron = env.variables.octiron

    env.macro(
        partial(
            link,
            octiron=octiron,
        ),
        name='link',
    )

    env.macro(
        partial(
            render,
            octiron=octiron,
        ),
        name='render',
    )

    env.macro(
        partial(
            query,
            instance=env.variables.graph,
        ),
        name='query',
    )

    env.macro(
        partial(
            url,
            graph=env.variables.graph,
        ),
        name='url',
    )

    env.filter(
        partial(
            url,
            graph=env.variables.graph,
        ), name='url',
    )

    env.filter(
        partial(
            label,
            graph=env.variables.graph,
        ),
        name='label',
    )

    env.macro(iri_to_url)
    env.macro(src_path_to_iri)

    env.filter(iri_to_url)

    env.filter(iri_by_page)
    env.macro(iri_by_page)

    # Update context with namespaces
    env.variables.update(octiron.namespaces)

    env.variables['URIRef'] = rdflib.URIRef

    return env
