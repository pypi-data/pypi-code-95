"""Code related to table header management.

- schema_sync=True option disables all errors relative to
    (missing|extra|mismatch) header errors.
- Validata want to:
  - emit a missing header error if a required column is missing
  - emit warnings if:
    - a non required column is missing
    - an extra column has been added
    - columns are disordered
"""


def structure_warning(code: str, name: str, message: str, field_name: str = ""):
    return {"code": code, "name": name, "message": message, "field_name": field_name}


def iter_structure_warnings(source_header, required_field_names, schema):
    """Iterate structure warnings in table."""
    schema_field_names = [field["name"] for field in schema.get("fields", [])]

    # missing optional fields
    for field_name in schema_field_names:
        if field_name not in source_header and field_name not in required_field_names:
            yield structure_warning(
                "missing-header-warn",
                "colonne manquante",
                f"Ajoutez la colonne manquante `{field_name}`.",
                field_name,
            )

    for h in source_header:
        if h not in schema_field_names:
            yield structure_warning(
                "extra-header-warn",
                "colonne surnuméraire",
                f"Retirez la colonne `{h}` non définie dans le schéma.",
                h,
            )

    if (
        set(source_header) == set(schema_field_names)
        and source_header != schema_field_names
    ):
        yield structure_warning(
            "disordered-header-warn",
            "colonnes désordonnées",
            (
                "Réordonnez les colonnes du fichier pour respecter le schéma :"
                f" {schema_field_names!r}."
            ),
        )
