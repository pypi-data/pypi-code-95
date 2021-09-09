import csv
import math
import re
from dataclasses import dataclass
from datetime import date
from datetime import datetime
from enum import Enum
from functools import partial
from pathlib import Path
from typing import Dict
from typing import Iterator
from typing import List

from toolz import pipe

COLS = {"Date opération", "Date valeur", "libellé", "Débit", "Crédit"}


class Method(Enum):
    USER = "user"
    HEURISTIC = "heuristic"
    AUTO = "auto"


class Category(Enum):
    AUTRE = "autre"
    COURSE = "course"
    LOISIR = "loisir"
    MAISON = "maison"
    RESTAURANT = "restaurant"
    TRANSPORT = "transport"
    VACANCES = "vacances"
    REVOIR = "revoir"


@dataclass
class Tag:
    """data model to store record of a tagged description"""

    method: Method
    description: str
    category: Category


@dataclass
class Tagger:
    tags: List[Tag]

    @classmethod
    def from_dict(cls, data: List[dict]):
        """each dict should have the following keys:
        - category
        - description
        - method
        """

        def to_tag(elt: dict):
            return Tag(
                Method[elt["method"].upper()],
                elt["description"],
                Category[elt["category"].upper()],
            )

        return Tagger([to_tag(elt) for elt in data])

    def guess(self, description: str) -> Category:
        """guess category from a bank cleaned hint

        note: comparaison are done casting lower() on string
        """

        def normalize(txt):
            return txt.lower()

        # call dynamodb on '/user + description with aws dyn boto3
        clean = description.strip()
        matched = [
            tag.category
            for tag in self.tags
            if normalize(clean) == normalize(tag.description)
        ]
        if matched:
            return matched.pop()
        else:
            return Category.AUTRE


@dataclass
class TidyRow:
    date: str
    mode: str
    description: str
    operation: str
    valeur: float
    category: Category = Category.AUTRE
    city: str = ""

    def update(self, tagger: Tagger):
        self.category = tagger.guess(self.description)


@dataclass
class Column:
    field: str
    label: str


def refresh_date(current: str, day: str, month: str, format="%d/%m/%Y") -> date:
    """merge `current` format with day and month"""
    reference = datetime.strptime(current, format)
    newyear = reference.year if reference.month >= int(month) else reference.year - 1
    return date(newyear, int(month), int(day))


def to_tidy_row(row: dict) -> TidyRow:
    """Transform a row from fortuneo csv dump
    to a standard format

    The following keys are expected in `row`:

    -"Date opération"
    -"Mode"
    -"libellé"
    -"Débit"
    -"Crédit"
    """
    if not is_valid(row):
        raise ValueError(f"Mismatch columns, expected {COLS}. Provided : {row.keys()}")
    operation = "debit" if row["Débit"] else "credit"
    valeur = row["Débit"] if operation == "debit" else row["Crédit"]
    # french format is usually something like 23,55
    valeur = float(valeur.replace(",", "."))
    # 'operation' field will handle meaning we don't need '+' or '-'
    valeur = math.fabs(valeur)
    # split description further
    parts = get_component(row["libellé"])
    if "jour" in parts:
        newdate = refresh_date(row["Date opération"], parts["jour"], parts["mois"])
        date = newdate.strftime("%Y-%m-%d")
    else:
        day, month, year = row["Date opération"].split("/")
        date = f"{year}-{month}-{day}"

    return TidyRow(
        date=date,
        mode=parts["mode"],
        description=parts["description"],
        operation=operation,
        valeur=valeur,
    )


def clean_empty(elt: dict) -> dict:
    """remove empty key"""
    return {k: v for k, v in elt.items() if k}


def is_valid(row: dict) -> bool:
    return row.keys() == COLS


def preprocess(rows: List[Dict]) -> List[Dict]:
    """correct basic malformed data and filter out corrupted one"""
    # FIXME
    cleaned = [clean_empty(row) for row in rows]
    return [row for row in cleaned if is_valid(row)]


def get_component(description: str) -> dict:
    """extract mode, jour & mois when applicable(carte) and description"""
    pattern = re.compile(
        r"""
    (?P<mode>^[a-z]+) # prlvt,carte, ...
    (\s(?P<jour>\d{2})/(?P<mois>\d{2}))? ## only for carte
    \s(?P<description>.*)
    """,
        re.VERBOSE,
    )
    match = pattern.match(description.lower())
    return {k: v for k, v in match.groupdict().items() if v} if match else {}


def read_csv(csvfile: Path) -> Iterator[TidyRow]:
    return pipe(
        csvfile.open(encoding="latin"),
        partial(csv.DictReader, delimiter=";"),
        # remove empty field
        partial(map, clean_empty),
        # reshape for easier usage
        partial(map, to_tidy_row),
    )
