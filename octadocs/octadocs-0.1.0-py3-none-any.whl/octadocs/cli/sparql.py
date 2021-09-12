import csv
import sys
from pathlib import Path
from typing import Optional

from octadocs.cli.formatters.csv import csv_print
from octadocs.cli.formatters.json import print_json
from octadocs.cli.formatters.pretty import pretty_print
from octadocs.octiron import Octiron
from octadocs.storage import DiskCacheStorage
from octadocs.types import QueryResultsFormat, SelectResult
from typer import Argument, Option, Typer

app = Typer(name='sparql')


def create_octiron() -> Octiron:
    octiron = Octiron(root_directory=Path.cwd() / 'docs')

    disk_cache_storage = DiskCacheStorage(octiron=octiron)
    disk_cache_storage.load()

    return octiron


@app.callback(invoke_without_command=True)
def sparql(
    fmt: QueryResultsFormat = Option(
        default=QueryResultsFormat.PRETTY,
        metavar='format',
    ),
    query_text: Optional[str] = Argument(
        None,
        metavar='query',
        help='SPARQL query text. Will be read from stdin if empty.',
    ),
) -> None:
    """Run a SPARQL query against the graph."""
    if query_text is None:
        query_text = sys.stdin.read()

    octiron = create_octiron()

    query_result = octiron.query(query_text)

    {
        QueryResultsFormat.CSV: csv_print,
        QueryResultsFormat.PRETTY: pretty_print,
        QueryResultsFormat.JSON: print_json,
    }[fmt](query_result)   # type: ignore
