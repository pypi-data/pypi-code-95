add_attribute("ChronologicalRelation", "start_date", commit=False)
add_attribute("ChronologicalRelation", "end_date")

for etype in ("AssociationRelation", "ChronologicalRelation", "HierarchicalRelation"):
    add_attribute(etype, "entry")

add_entity_type("NameEntry")
with cnx.deny_all_hooks_but("metadata"):
    for record in rql(
        "Any X,XN WHERE X is AuthorityRecord, X name XN", ask_confirm=False
    ).entities():
        create_entity(
            "NameEntry",
            parts=record.name,
            form_variant=u"authorized",
            name_entry_for=record,
            ask_confirm=False,
        )
commit(ask_confirm=False)
drop_attribute("AuthorityRecord", "name")

add_attribute("Activity", "agent")

sync_schema_props_perms("has_citation", syncperms=False)
