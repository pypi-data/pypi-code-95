"""
    Year Interval Value check

    Vérifie que l'on a bien une valeur du type "aaaa/aaaa" avec la première année
    inférieure à la seconde ou une année seulement
    (si le paramètre allow-year-only est activé)

    Messages d'erreur attendus :
    - Si la valeur n'est pas du type ^\\d{4}/\\d{4}$ (ex : "toto")
      - La valeur "toto" n'a pas le format attendu pour une période (AAAA/AAAA).
    - Si les deux années sont identiques (ex : "2017/2017")
      - Période "2017/2017 invalide. Les deux années doivent être différentes).
    - Si la deuxième année est inférieure à la première (ex : "2017/2012")
      - Période "2017/2012" invalide. La deuxième année doit être postérieure
        à la première (2012/2017).

    Pierre Dittgen, Jailbreak
"""
import re

from frictionless import Check, errors

YEAR_INTERVAL_RE = re.compile(r"^(\d{4})/(\d{4})$")
YEAR_RE = re.compile(r"^\d{4}$")

# Module API


class YearIntervalValueError(errors.CellError):
    """Custom error."""

    code = "year-interval-value"
    name = "Année ou intervalle d'années"
    tags = ["#body"]
    template = "L'année ou l'intervalle d'année '{cell}' est incorrect ({note})."
    description = "Année ou intervalle d'années"


class YearIntervalValue(Check):
    """Year Interval Value check class."""

    possible_Errors = [YearIntervalValueError]  # type: ignore

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")
        self.__allow_year_only = self.get("allow-year-only") in ("true", "yes")

    def validate_start(self):
        if self.__column not in self.resource.schema.field_names:
            note = f"La colonne {self.__column!r} est manquante."
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell_value = row[self.__column]

        # Empty cell, don't check!
        if not cell_value:
            return

        # Checks for interval format
        rm = YEAR_INTERVAL_RE.match(cell_value)
        if not rm:

            # Not an interval, is this a year only?
            if self.__allow_year_only:
                ym = YEAR_RE.match(cell_value)

                # No -> add error
                if not ym:
                    note = "format attendu: année (AAAA) ou intervale (AAAA/AAAA)"
                    yield YearIntervalValueError.from_row(
                        row, note=note, field_name=self.__column
                    )

                # Year ok
                return

            # not a period -> add error
            note = "format attendu: AAAA/AAAA"
            yield YearIntervalValueError.from_row(
                row, note=note, field_name=self.__column
            )
            return

        year1 = int(rm.group(1))
        year2 = int(rm.group(2))
        if year1 == year2:
            note = "les deux années doivent être différentes"
            yield YearIntervalValueError.from_row(
                row, note=note, field_name=self.__column
            )
            return

        if year1 > year2:
            note = (
                f"la deuxième année ({year1}) doit être postérieure"
                " à la première ({year2})"
            )
            yield YearIntervalValueError.from_row(
                row, note=note, field_name=self.__column
            )
            return

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {
            "column": {"type": "string"},
            "allow-year-only": {"type": "string"},
        },
    }
