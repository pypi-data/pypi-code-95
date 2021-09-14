for rtype in (
    "association_from",
    "association_to",
    "chronological_predecessor",
    "chronological_successor",
    "hierarchical_parent",
    "hierarchical_child",
):
    sync_schema_props_perms(rtype)
