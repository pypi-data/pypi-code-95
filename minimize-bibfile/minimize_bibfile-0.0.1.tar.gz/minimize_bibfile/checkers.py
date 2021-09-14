"""Utilities to validate bib files."""
from typing import List, Dict, Union
from collections import Counter
from string import punctuation
from jaro import jaro_winkler_metric
import bibtexparser


def check_all_entries_have_fields(entries: List[Dict], fields: Union[str, List[str]]):
    """Raise error if entries are found without given field(s).

    Parameters
    ------------------------------
    entries: List[Dict]
        The entries to check.
    fields: Union[str, List[str]]
        The fields to check for existance.
    """
    if isinstance(fields, str):
        fields = [fields]
    for entry in entries:
        for field in fields:
            if field not in entry:
                raise ValueError(
                    (
                        "Requested field {} does not exist "
                        "in the provided entry: {}."
                    ).format(
                        field,
                        entry
                    )
                )


def normalize_text(text: str) -> str:
    """Return normalized text.

    Parameters
    --------------------------
    text: str
        The text to normalize.

    Returns
    --------------------------
    The normalized text
    """
    lower_text = text.lower()
    for symbol in punctuation:
        lower_text = lower_text.replace(symbol, " ")
    return " ".join(lower_text.split())


def check_for_complete_duplicates(
    entries: List[Dict],
    fields: Union[str, List[str]]
):
    """Check for duplicated fields.

    Parameters
    ---------------------------
    entries: List[Dict]
        The entries to validate.
    fields: Union[str, List[str]]
        The fields to check against.
    """
    if isinstance(fields, str):
        fields = [fields]

    check_all_entries_have_fields(entries, fields)

    for field in fields:
        unique_field_values = Counter([
            normalize_text(entry[field])
            for entry in entries
        ])
        for field_value, count in unique_field_values.items():
            if count > 1:
                raise ValueError(
                    (
                        "Found {} entries for the value `{}` "
                        "from field {}."
                    ).format(
                        count,
                        field_value,
                        field
                    )
                )


def check_for_near_duplicates(
    entries: List[Dict],
    fields: Union[str, List[str]],
    threshold: float = 0.9
):
    """Check for near duplicates using Jaro-Wrinkler.

    Parameters
    ---------------------------
    entries: List[Dict]
        The entries to validate.
    fields: Union[str, List[str]]
        The fields to check against.
    threshold: float = 0.9
        The threshold over which we declare the presence of a duplicate.
    """
    if isinstance(fields, str):
        fields = [fields]

    check_all_entries_have_fields(entries, fields)

    for field in fields:
        for i, entry in enumerate(entries):
            field_value = normalize_text(entry[field])
            for j, inner_entry in enumerate(entries):
                if i <= j:
                    continue
                inner_field_value = normalize_text(inner_entry[field])
                score = jaro_winkler_metric(field_value, inner_field_value)
                if score > threshold:
                    print(
                        (
                            "The entries {} values \n - {}\n - {}\n "
                            "have a Jaro-Wrinkler score of {}."
                        ).format(
                            field,
                            field_value,
                            inner_field_value,
                            score
                        )
                    )


def general_bib_check(path: str):
    """Runs check for the file at given path.

    Parameters
    -----------------------------
    path: str
        The path to the file to load and check.
    """
    with open(path) as f:
        bib_database = bibtexparser.loads(f.read())

    entries = bib_database.entries

    check_for_complete_duplicates(
        entries,
        "title"
    )

    check_for_near_duplicates(
        entries,
        "title"
    )
