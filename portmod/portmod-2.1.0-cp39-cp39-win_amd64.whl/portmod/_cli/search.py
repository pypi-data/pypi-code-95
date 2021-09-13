# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from collections import defaultdict
from typing import Dict, List

from portmod.merge import configure
from portmod.prompt import prompt_num_multi
from portmod.query import display_search_results, query
from portmodlib.colour import bright, lblue
from portmodlib.l10n import l10n

from .pybuild import Pybuild


def search_main(args):
    pkgs = list(
        query(
            ["NAME", "ATOM", "DESC"],
            " ".join(args.query),
            strip=True,
            squelch_sep=True,
            insensitive=True,
        )
    )
    grouped: Dict[str, List[Pybuild]] = defaultdict(list)
    for pkg in pkgs:
        grouped[pkg.CPN].append(pkg)

    sortedgroups = sorted(grouped.values(), key=lambda group: group[0].CPN)

    display_search_results(sortedgroups, numbers=True)

    selection = selection_prompt([group[0].CPN for group in sortedgroups])
    configure(selection)


def selection_prompt(atoms):
    # Allow selecting numbers between 0 and the number of mods
    selection = prompt_num_multi(
        bright(lblue(":: ")) + bright("Packages to install (eg: 1,2,3)"), len(atoms)
    )
    # Iterate through the selected numbers, and get
    # the atoms that correspond to those numbers
    mod_selection = [atoms[number - 1] for number in selection]
    return [index for index in mod_selection]


def add_search_parser(subparsers, parents):
    parser = subparsers.add_parser("search", help=l10n("search-help"), parents=parents)

    parser.add_argument(
        "query",
        nargs="+",
        metavar=l10n("query-placeholder"),
        help=l10n("search-query-help"),
    )
    parser.set_defaults(func=search_main)
