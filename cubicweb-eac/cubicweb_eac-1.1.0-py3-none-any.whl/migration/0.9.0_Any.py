add_entity_type("HistoricalEvent")
add_entity_type("Convention")
add_entity_type("ParallelNames")
add_entity_type("EACFunctionRelation")
add_entity_type("DateEntity")
add_entity_type("PlaceEntry")
add_entity_type("IdentityRelation")
add_entity_type("FamilyRelation")

# Attributes to update
add_attribute("EACResourceRelation", "xml_attributes")
add_attribute("EACResourceRelation", "relation_entry")
add_attribute("PostalAddress", "raw_address")

add_attribute("History", "abstract")

# migrate AgentPlace

for (agent_eid, name, exturi_eid,) in cnx.execute(
    "Any X, N, E WHERE X is AgentPlace, X name N, X equivalent_concept E?"
):
    cnx.create_entity(
        "PlaceEntry",
        place=name,
        reverse_place_entry_relation=agent_eid,
        equivalent_concept=exturi_eid,
    )

drop_attribute("AgentPlace", "name")
drop_relation_definition("AgentPlace", "equivalent_concept", ("ExternalUri", "Concept"))

cnx.commit()


for attrib in (
    "language",
    "preferred_form",
    "alternative_form",
    "authorized_form",
    "script_code",
):
    add_attribute("NameEntry", attrib)

add_relation_type("date_relation")

for etype in (
    "AssociationRelation",
    "ChronologicalRelation",
    "HierarchicalRelation",
    "Mandate",
    "LegalStatus",
    "HistoricalEvent",
    "Occupation",
    "EACFunctionRelation",
    "EACResourceRelation",
):
    subjrels = [s.type for s in cnx.vreg.schema.eschema(etype).subjrels]
    if "start_date" and "end_date" in subjrels:
        rql(
            """INSERT DateEntity D:
            E date_relation D, D start_date SD, D end_date ED WHERE
            E is {},
            E start_date SD, E end_date ED""".format(
                etype
            )
        )
        drop_attribute(etype, "start_date")
        drop_attribute(etype, "end_date")

add_relation_definition("NameEntry", "date_relation", "DateEntity")
add_relation_definition("Structure", "has_citation", "Citation")

for etype in (
    "GeneralContext",
    "Mandate",
    "Occupation",
    "History",
    "AgentFunction",
    "LegalStatus",
    "AgentPlace",
    "Structure",
):
    add_attribute(etype, "items")

add_relation_type("place_entry_relation")

add_attribute("Activity", "agent_type")

add_attribute("AuthorityRecord", "languages")

sync_schema_props_perms("record_id")

add_relation_definition(
    "EACResourceRelation", "resource_relation_resource", "AuthorityRecord"
)

add_relation_definition(
    "EACFunctionRelation", "function_relation_function", "AuthorityRecord"
)
