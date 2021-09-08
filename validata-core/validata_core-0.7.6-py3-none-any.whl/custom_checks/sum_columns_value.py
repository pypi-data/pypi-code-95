import decimal
import re

from frictionless import Check, errors

"""
    Sum columns value check

    Pour une colonne donnée (column) et une liste de colonnes (columns),
    on vérifie que la première colonne contient bien
    la somme des valeurs entières des autres colonnes

    La vérification ne s'effectue pas si l'ensemble des colonnes est vide

    Paramètres :
    - column : le nom de la première colonne contenant la somme
    - columns : le nom des colonnes contenant les valeurs à ajouter

    Messages d'erreur attendus :
    - La valeur de la colonne {col} [val] n'est pas entière, il n'est pas possible
        de vérifier que {col} = {col1} + {col2} + ...
    - La valeur des colonnes {col1}, {col2}, ... ne sont pas entières,
        il n'est pas possible de vérifier que {col} = {col1} + {col2} + ...
    - La somme des valeurs des colonnes {col1}, {col2}, ... est {sum},
        ce nombre est différent de celui attendu dans {col} [val]

    Pierre Dittgen, Jailbreak
"""

# Module API

INT_RE = re.compile(r"^\d+$")


class SumColumnsValueError(errors.CellError):
    """Custom error."""

    code = "sum-columns-value"
    name = "Somme de colonnes"
    tags = ["#body"]
    template = "La somme de colonne ne peut être calculée ({note})."
    description = "Somme de colonnes"


class SumColumnsValue(Check):
    """Sum columns value check."""

    possible_Errors = [SumColumnsValueError]

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")
        self.__columns = self.get("columns")
        self.__all_columns = [self.__column] + self.__columns

    def validate_start(self):
        if self.__column not in self.resource.schema.field_names:
            note = f"la colonne {self.__column!r} est manquante"
            yield errors.TaskError(note=note)
        elif len(self.__columns) < 2:
            note = "le nombre de colonnes est insuffisant pour l'addition"
            yield errors.TaskError(note=note)
        else:
            for col in self.__columns:
                if col not in self.resource.schema.field_names:
                    note = f"la colonne {col!r} est manquante."
                    yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell_values = [row[col] for col in self.__all_columns]

        # Don't yell if one of the cells is empty
        if not all(valued(cell_value) for cell_value in cell_values):
            return

        # Checks that all values are integer
        # => already checked by schema

        # Check sum
        computed_sum = sum(int(row[col]) for col in self.__columns)
        column_sum = int(row[self.__column])
        if computed_sum != column_sum:
            column = self.__column
            column_value_list = ", ".join(
                f"{col} ({int(row[col])})" for col in self.__columns
            )
            note = (
                f"la somme des valeurs des colonnes {column_value_list!r} est"
                f" `{computed_sum}`, ce nombre est différent de celui trouvé"
                f" dans la colonne {column!r} (`{column_sum}`)"
            )
            yield SumColumnsValueError.from_row(row, note=note, field_name=column)

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column", "columns"],
        "properties": {"column": {"type": "string"}, "columns": {"type": "array"}},
    }


def valued(val):
    """ Return True if the given string value is not empty """
    return val != "" and val is not None


def is_int(value):
    """ Return True if the given string contains an integer """
    if isinstance(value, int) or isinstance(value, decimal.Decimal):
        return True
    if isinstance(value, str):
        return INT_RE.match(value)
    return False
