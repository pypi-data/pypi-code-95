from domain.generic_replacements.replacement import Replacement


def replacements_to_json(replacements: list[Replacement]) -> list[dict]:
    return list(
        map(
            lambda replacement: replacement.to_json(),
            replacements
        )
    )
