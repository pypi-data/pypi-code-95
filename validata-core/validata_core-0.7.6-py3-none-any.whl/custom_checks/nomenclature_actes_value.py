"""
    Comme indiqué par Loïc Haÿ dans son mail du 5/7/2018

> Document de référence dans les spécifications SCDL :
> http://www.moselle.gouv.fr/content/download/1107/7994/file/nomenclature.pdf
>
> Dans la nomenclature Actes, les valeurs avant le "/" sont :
>
> Commande publique
> Urbanisme
> Domaine et patrimoine
> Fonction publique
> Institutions et vie politique
> Libertés publiques et pouvoirs de police
> Finances locales
> Domaines de compétences par thèmes
> Autres domaines de compétences
>
> Le custom check devra accepter minuscules et majuscules, accents et sans accents ...

    Pierre Dittgen, JailBreak
"""
import unicodedata

from frictionless import Check, errors

# Module API

AUTHORIZED_VALUES = [
    "Commande publique",
    "Urbanisme",
    "Domaine et patrimoine",
    "Fonction publique",
    "Institutions et vie politique",
    "Libertés publiques et pouvoirs de police",
    "Finances locales",
    "Domaines de compétences par thèmes",
    "Autres domaines de compétences",
]


class NomenclatureActesValueError(errors.CellError):
    """Custom error."""

    code = "nomenclature-actes-value"
    name = "Actes de nomenclature"
    tags = ["#body"]
    template = (
        "La valeur {cell!r} ne respecte pas le format des nomenclatures d'actes"
        " ({note})"
    )
    description = (
        "Les nomenclatures d'actes doivent commencer"
        " par un préfixe particulier suivi d'une oblique (/)"
    )


class NomenclatureActesValue(Check):

    possible_Errors = [NomenclatureActesValueError]  # type: ignore

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__column = self.get("column")
        self.__nomenclatures = set(map(norm_str, AUTHORIZED_VALUES))

    def validate_start(self):
        if self.__column not in self.resource.schema.field_names:
            note = f"La colonne {self.__column!r} est manquante." ""
            yield errors.TaskError(note=note)

    def validate_row(self, row):
        cell_value = row[self.__column]
        if not cell_value:
            return

        if "/" not in cell_value:
            note = "le signe oblique « / » est manquant"
            yield NomenclatureActesValueError.from_row(
                row, note=note, field_name=self.__column
            )
            return

        nomenc = cell_value[: cell_value.find("/")]
        if norm_str(nomenc) not in self.__nomenclatures:
            note = f"le préfixe de nomenclature Actes {nomenc!r} n'est pas reconnu"
            yield NomenclatureActesValueError.from_row(
                row, note=note, field_name=self.__column
            )
            return

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["column"],
        "properties": {"column": {"type": "string"}},
    }


def norm_str(s):
    """ Normalize string, i.e. removing accents and turning into lowercases """
    return "".join(
        c
        for c in unicodedata.normalize("NFD", s.lower())
        if unicodedata.category(c) != "Mn"
    )
