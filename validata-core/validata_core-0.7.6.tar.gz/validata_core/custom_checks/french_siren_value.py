import stdnum.fr.siren
from frictionless import Check, errors


class FrenchSirenValueError(errors.CellError):
    """Custom error."""

    code = "french-siren-value"
    name = "Numéro SIREN invalide"
    tags = ["#body"]
    template = "La valeur {cell} n'est pas un numéro SIREN français valide."
    description = (
        "Le numéro de SIREN indiqué n'est pas valide selon la définition"
        " de l'[INSEE](https://www.insee.fr/fr/metadonnees/definition/c2047)."
    )


class FrenchSirenValue(Check):
    """Check french SIREN number validity."""

    possible_Errors = [FrenchSirenValueError]  # type: ignore

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")

    def validate_start(self):
        if self.__column not in self.resource.schema.field_names:
            note = f"La colonne {self.__column!r} est manquante."
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell_value = row[self.__column]

        # Empty cell, don't check!
        if not cell_value:
            return

        if not stdnum.fr.siren.is_valid(cell_value):
            yield FrenchSirenValueError.from_row(row, note="", field_name=self.__column)

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }
