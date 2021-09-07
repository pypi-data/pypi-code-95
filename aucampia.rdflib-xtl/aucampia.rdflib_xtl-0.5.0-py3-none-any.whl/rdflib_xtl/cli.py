#!/usr/bin/env python3
# vim: set filetype=python sts=4 ts=4 sw=4 expandtab tw=88 cc=+1:
# vim: set filetype=python tw=88 cc=+1:

import enum
import logging
import os
import pathlib
import sys
from typing import Any, ClassVar, List, Optional, Set, Type, TypeVar, cast

import click
import owlrl  # type: ignore[import]
import rdflib  # type: ignore[import]
import rdflib.namespace as rlns  # type: ignore[import]
import rdflib.plugins.sparql as rlsparql  # type: ignore[import]
import rdflib.query  # type: ignore[import]
import typer
import yaml

LOGGER = logging.getLogger(__name__)

GenericT = TypeVar("GenericT")


def static_init(cls: Type[Any]) -> Type[Any]:
    if getattr(cls, "static_init", None):
        cast(Any, cls).static_init()
    return cls


@static_init
class ReasonerClosureClass(enum.Enum):
    key_strings: ClassVar[Set[str]]

    RDFS_Semantics = owlrl.CombinedClosure.RDFS_Semantics
    OWLRL_Semantics = owlrl.CombinedClosure.OWLRL_Semantics
    RDFS_OWLRL_Semantics = owlrl.CombinedClosure.RDFS_OWLRL_Semantics

    @classmethod
    def static_init(cls) -> None:
        setattr(cls, "key_strings", set())
        for enm in cls:
            cls.key_strings.add(enm.name)  # type: ignore

    @classmethod
    def from_string(cls, string: str) -> owlrl.Closure.Core:
        if string not in cls.key_strings:  # type: ignore
            raise ValueError(
                "Invalid closure class name {}. Must be one of {}".format(
                    string, ", ".join(cls.key_strings)  # type: ignore
                )
            )
        return cls[string].value


"""
https://click.palletsprojects.com/en/7.x/api/#parameters
https://click.palletsprojects.com/en/7.x/options/
https://click.palletsprojects.com/en/7.x/arguments/
"""

cli = typer.Typer()


@cli.callback()
def cli_callback(
    ctx: typer.Context, verbosity: int = typer.Option(0, "--verbose", "-v", count=True)
) -> None:
    if verbosity is not None:
        root_logger = logging.getLogger("")
        root_logger.propagate = True
        new_level = (
            root_logger.getEffectiveLevel()
            - (min(1, verbosity)) * 10
            - min(max(0, verbosity - 1), 9) * 1
        )
        root_logger.setLevel(new_level)

    LOGGER.debug(
        "entry: ctx.parent.params = %s, ctx.params = %s",
        ({} if ctx.parent is None else ctx.parent.params),
        ctx.params,
    )
    LOGGER.debug(
        "logging.level = %s, LOGGER.level = %s",
        logging.getLogger("").getEffectiveLevel(),
        LOGGER.getEffectiveLevel(),
    )


@cli.command("reason")
def cli_reason(
    ctx: click.Context,
    reasoner_closure_class: str = typer.Option(
        "RDFS_OWLRL_Semantics", "--closure-class", "--cc"
    ),
    reasoner_options: str = typer.Option("", "--options", "--opts"),
    input_format: Optional[str] = typer.Option(None, "--input-format", "--if"),
    output_format: str = typer.Option("turtle", "--output-format", "--of"),
    input: Optional[List[str]] = typer.Argument(None),
) -> None:
    LOGGER.debug(
        "entry: ctx.parent.params = %s, ctx.params = %s",
        ({} if ctx.parent is None else ctx.parent.params),
        ctx.params,
    )

    graph = rdflib.Graph()
    data_files = [] if input is None else input
    for data_file in data_files:
        fmt = rdflib.util.guess_format(data_file)
        LOGGER.debug("Loading %s with format %s", data_file, fmt)
        graph.parse(source=data_file, format=input_format)

    reasoner_options = reasoner_options
    closure_class_name = reasoner_closure_class
    closure_class = ReasonerClosureClass.from_string(closure_class_name)
    reasoner = owlrl.DeductiveClosure(
        closure_class, **yaml.safe_load(reasoner_options or "{}")
    )
    reasoner.expand(graph)
    sys.stdout.write(graph.serialize(format="turtle").decode("utf-8"))


@cli.command("sparql")
def cli_sparql(
    ctx: click.Context,
    query_string: Optional[str] = typer.Option(None, "--query", "-q"),
    query_file: Optional[str] = typer.Option(None, "--query-file", "-Q"),
    default_prefixes: bool = typer.Option(
        True, "--default-prefixes/--no-default-prefixes", "--dp/--no-dp", is_flag=True
    ),
    input_prefixes: bool = typer.Option(
        True, "--input-prefixes/--no-input-prefixes", "--ip/--no-ip", is_flag=True
    ),
    prefixes: List[str] = typer.Option([], "--prefix", "-p"),
    prefix_files: List[str] = typer.Option([], "--prefix-file", "-P"),
    reason: bool = typer.Option(False, "--reason/--no-reason", is_flag=True),
    reasoner_closure_class: str = typer.Option(
        "RDFS_OWLRL_Semantics", "--reasoner-closure-class", "--reasoner-cc"
    ),
    reasoner_options: Optional[str] = typer.Option(
        None, "--reasoner-options", "--reasoner-opts"
    ),
    input_format: Optional[str] = typer.Option(None, "--input-format", "--if"),
    output_format: Optional[str] = typer.Option(None, "--output-format", "--of"),
    input: Optional[List[str]] = typer.Argument(None),
) -> None:
    LOGGER.debug(
        "entry: ctx.parent.params = %s, ctx.params = %s",
        ({} if ctx.parent is None else ctx.parent.params),
        ctx.params,
    )

    if query_string is None and query_file is None:
        raise click.UsageError("need a query or a query file", ctx)

    if query_string is None:
        assert query_file is not None
        query_string = pathlib.Path(query_file).read_text()

    graph = rdflib.Graph()
    data_files = [] if input is None else input
    for data_file in data_files:
        fmt = rdflib.util.guess_format(data_file)
        LOGGER.debug("Loading %s with format %s", data_file, fmt)
        graph.parse(source=data_file, format=input_format)

    if default_prefixes:
        initNs = {
            "dc": rlns.DC,
            "dcterms": rlns.DCTERMS,
            "fn": rlns.Namespace("http://www.w3.org/2005/xpath-functions#"),
            "foaf": rlns.FOAF,
            "geo": rlns.Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#"),
            "owl": rlns.OWL,
            "rdf": rlns.RDF,
            "rdfs": rlns.RDFS,
            "sfn": rlns.Namespace("http://www.w3.org/ns/sparql#"),
            "skos": rlns.SKOS,
            "vann": rlns.Namespace("http://purl.org/vocab/vann/"),
            "xml": rlns.Namespace("http://www.w3.org/XML/1998/namespace#"),
            "xsd": rlns.XSD,
            "cc": rlns.Namespace("http://creativecommons.org/ns#"),
        }
    else:
        initNs = {}

    if input_prefixes:
        for prefix, uri in graph.namespaces():
            initNs[prefix] = uri

    query = rlsparql.prepareQuery(query_string, initNs=initNs)

    if reason:
        reasoner_options = reasoner_options
        closure_class_name = reasoner_closure_class
        closure_class = ReasonerClosureClass.from_string(closure_class_name)
        reasoner = owlrl.DeductiveClosure(
            closure_class, **yaml.safe_load(reasoner_options or "{}")
        )
        reasoner.expand(graph)

    qrh = QueryResultHelper(graph.query(query))
    LOGGER.debug("qrh.instance = %s", qrh.instance)
    if output_format is None:
        output_format = "text/turtle" if qrh.is_rdf else "text/csv"

    if qrh.is_rdf:
        result_graph = qrh.instance.graph
        for prefix, uri in graph.namespaces():
            result_graph.bind(prefix, uri, False, False)

    sys.stdout.buffer.write(qrh.instance.serialize(format=output_format))


def fomat_to_mine(format_str: str) -> str:
    return format_str


class QueryResultHelper:
    instance: rdflib.query.Result

    def __init__(self, instance: rdflib.query.Result):
        self.instance = instance

    @property
    def is_rdf(self) -> bool:
        return self.instance.type in ("CONSTRUCT", "DESCRIBE")

    def supported_formats(self) -> Set[str]:
        if self.is_rdf:
            result = set(
                [
                    "application/ld+json",
                    "application/rdf+xml",
                    "text/turtle",
                    "application/n-triples",
                    "application/n-quads",
                    "application/trix",
                ]
            )
        else:
            result = set(
                [
                    "text/csv",
                    "text/plain",
                    # "text/tab-separated-values",
                    "application/sparql-results+json",
                    "application/sparql-results+xml",
                ]
            )
        return result


def main(*args: Any, **kwargs: Any) -> Any:
    logging.basicConfig(
        level=os.environ.get("PYLOGGING_LEVEL", logging.INFO),
        stream=sys.stderr,
        datefmt="%Y-%m-%dT%H:%M:%S",
        format=(
            "%(asctime)s.%(msecs)03d %(process)d %(thread)d %(levelno)03d:%(levelname)-8s "
            "%(name)-12s %(module)s:%(lineno)s:%(funcName)s %(message)s"
        ),
    )

    return cli(obj={}, *args, **kwargs)


if __name__ == "__main__":
    main()
