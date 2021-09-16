from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Union

from rdflib import Graph, ConjunctiveGraph
from rdflib.plugins.sparql.processor import SPARQLResult
from rdflib.term import Node, Variable, Identifier

SelectRow = Dict[str, Node]


class SelectResult(List[SelectRow]):
    """Result of a SPARQL SELECT."""


QueryResult = Union[
    SelectResult,   # SELECT
    Graph,          # CONSTRUCT
    bool,           # ASK
]


def _format_query_bindings(
    bindings: List[Dict[Variable, Identifier]],
) -> SelectResult:
    """
    Format bindings before returning them.

    Converts Variable to str for ease of addressing.
    """
    return SelectResult([
        {
            str(variable_name): rdf_value
            for variable_name, rdf_value
            in row.items()
        }
        for row in bindings
    ])


@dataclass(init=False)
class LDFlex:
    """Fluent interface to a semantic graph."""

    graph: Union[Graph, Path]

    def __init__(self, graph: Union[Graph, Path]):
        """Initialize the graph."""
        if isinstance(graph, Graph):
            self.graph = graph

        else:
            self.graph = ConjunctiveGraph()
            self.graph.parse(
                data=graph.read_text(),
                format='json-ld',
            )

    def query(
        self,
        query_text: str,
        **kwargs: str,
    ) -> QueryResult:
        """Run SPARQL SELECT, CONSTRUCT, or ASK query."""
        sparql_result: SPARQLResult = self.graph.query(
            query_text,
            initBindings=kwargs,
        )

        if sparql_result.askAnswer is not None:
            return sparql_result.askAnswer

        if sparql_result.graph is not None:
            graph: Graph = sparql_result.graph
            for prefix, namespace in self.graph.namespaces():
                graph.bind(prefix, namespace)

            return graph

        return _format_query_bindings(sparql_result.bindings)
