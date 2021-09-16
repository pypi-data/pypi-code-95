import itertools
from datetime import date
from typing import Union

from classes import typeclass
from more_itertools import consume

from iolanta.cli.pretty_print import render_literal_value
from octadocs.types import QueryResult, SelectResult
from rdflib import BNode, Graph, Literal, URIRef
from rich.console import Console
from rich.table import Table


@typeclass
def pretty_print_value(rdflib_value: Union[URIRef, Literal, BNode]) -> str:
    ...


@pretty_print_value.instance(URIRef)
def _pretty_print_value_uri_ref(uriref: URIRef):
    """Format URI Ref."""
    return f'🔗 {uriref}'


@pretty_print_value.instance(Literal)
def _pretty_print_literal(literal: Literal):
    """Render a literal."""
    return render_literal_value(literal.value)


@pretty_print_value.instance(BNode)
def _pretty_print_bnode(bnode: BNode):
    """Print a blank node."""
    return f'😶 {bnode}'


@typeclass
def pretty_print(query_result: QueryResult):
    """Pretty print query result."""


@pretty_print.instance(SelectResult)
def _pretty_print_select_result(select_result: SelectResult):
    """Print a SPARQL query result in style."""
    if not select_result:
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
    )

    first_row = select_result[0]

    consume(map(table.add_column, first_row.keys()))
    consume(itertools.starmap(
        table.add_row,
        [
            map(
                pretty_print_value,
                row.values(),
            )
            for row in select_result
        ],
    ))

    Console().print(table)


@pretty_print.instance(Graph)
def _pretty_construct(graph: Graph):
    if not graph:
        return

    table = Table(
        show_header=True,
        header_style="bold magenta",
    )

    consume(map(table.add_column, ('Subject', 'Predicate', 'Object')))

    consume(itertools.starmap(
        table.add_row,
        [
            map(
                pretty_print_value,
                triple,
            )
            for triple in graph
        ],
    ))

    Console().print(table)
