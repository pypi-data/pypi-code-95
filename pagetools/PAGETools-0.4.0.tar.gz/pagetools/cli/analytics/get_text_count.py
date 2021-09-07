from pagetools.src.utils import filesystem
from pagetools.src.utils.constants import TEXT_COUNT_SUPPORTED_ELEMS

from pagetools.src.Page import Page

import csv
from pathlib import Path

from rich.console import Console
from rich.table import Table

import click

console = Console(width=50)


@click.command("get_text_count",
               help="Returns the amount of text equiv elements in certain elements for certain indices.")
@click.argument("files", nargs=-1, required=True)
@click.option("-e", "--element", multiple=True, type=click.Choice(TEXT_COUNT_SUPPORTED_ELEMS),
              default=TEXT_COUNT_SUPPORTED_ELEMS)
@click.option("-i", "--index", multiple=True, required=True,
              help="Specifies which TextEquiv[@index] elements are taken into consideration. "
                   "Allowed values are [0-9] and 'None' for TextEquiv[not(@index)]")
@click.option("-so", "--stats-out", help="Output path for the detailed stats csv file.")
def get_text_count_cli(files: list[str], element: list[str], index: list[str], stats_out: str):
    # TODO: Needs refactoring. Was implemented fast for a urgent use case.
    total_counter = 0
    general_stats = {e: {"empty": 0, "non-empty": 0} for e in element}

    detailed_stats = []

    collected_files = filesystem.parse_file_input(files)

    for file in collected_files:
        page = Page(file)

        root = page.get_tree(True)

        if root is None:
            continue

        for elem in element:
            update_empty_non_empty(page, elem, general_stats)

            for idx in index:
                if index == "None":
                    xpath = f".//page:{elem}/page:TextEquiv[not(@index)]"
                else:
                    xpath = f'.//page:{elem}/page:TextEquiv[@index="{idx}"]'

                hits = len(root.xpath(xpath, namespaces=page.get_ns()))

                total_counter += hits
                detailed_stats.append({"page": file, "element": elem, "index": idx, "hits": hits})
    idx_hits = get_index_hits(index, detailed_stats)
    elem_hits = get_elem_hits(element, detailed_stats)

    console.print(f"Total count: {total_counter}", style="bold")
    console.rule(style="white")

    indices_table = Table(title="Count per index")
    indices_table.add_column("Index")
    indices_table.add_column("Count")
    for idx in idx_hits:
        indices_table.add_row(str(idx[0]), str(idx[1]))
    console.print(indices_table)
    console.rule(style="white")

    element_table = Table(title="Count per element (considering indices)")
    element_table.add_column("Element")
    element_table.add_column("Count")
    for elem in elem_hits:
        element_table.add_row(str(elem[0]), str(elem[1]))
    console.print(element_table)
    console.rule(style="white")

    general_stats_table = Table(title="General statistics")
    general_stats_table.add_column("Element")
    general_stats_table.add_column("# Total")
    general_stats_table.add_column("# Non-empty")
    general_stats_table.add_column("# Empty")
    for key, value in general_stats.items():
        general_stats_table.add_row(key,
                                    str(value["empty"] + value["non-empty"]),
                                    str(value["non-empty"]),
                                    str(value["empty"]))
    console.print(general_stats_table)
    if stats_out:
        serialize_stats(detailed_stats, stats_out)


def get_index_hits(index: list[str], stats: list[dict]) -> list[tuple]:
    idx_hits = []
    for idx in index:
        counter = 0
        for entry in stats:
            if entry["index"] == idx:
                counter += entry["hits"]
        idx_hits.append((idx, counter))
    return idx_hits


def get_elem_hits(elements: list[str], stats: list[dict]) -> list[tuple]:
    elem_hits = []
    for elem in elements:
        counter = 0
        for entry in stats:
            if entry["element"] == elem:
                counter += entry["hits"]
        elem_hits.append((elem, counter))
    return elem_hits


def update_empty_non_empty(page: Page, elem: str, general_stats: dict):
    root = page.get_tree(True)
    ns = page.get_ns()

    nodes = root.xpath(f".//page:{elem}", namespaces=ns)
    for node in nodes:
        empty = len(node.xpath("./page:TextEquiv/page:Unicode[string-length(text()) = 0]", namespaces=ns))
        non_empty = len(node.xpath("./page:TextEquiv/page:Unicode[string-length(text()) > 0]", namespaces=ns))

        if empty:
            general_stats[elem]["empty"] += 1
        elif non_empty:
            general_stats[elem]["non-empty"] += 1


def serialize_stats(stats: list[dict], stats_out: str):
    with Path(stats_out).open("w") as csvfile:
        stats_writer = csv.writer(csvfile,
                                  delimiter=',',
                                  quotechar='"',
                                  quoting=csv.QUOTE_ALL)
        header = ["page", "element", "index", "count"]
        stats_writer.writerow(header)
        for entry in stats:
            stats_writer.writerow([entry["page"], entry["element"], entry["index"], entry["hits"]])


if __name__ == "__main__":
    get_text_count_cli()
