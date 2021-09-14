from cubicweb_compound import utils
from cubicweb_eac import AuthorityRecordGraph

add_cube("compound")

graph = AuthorityRecordGraph(schema)
structure = graph.parent_structure("AuthorityRecord")

optionals = utils.optional_relations(schema, structure)
for child in structure:
    sync_schema_props_perms(child, syncprops=False)

for rdef, parent_role in utils.mandatory_rdefs(schema, structure):
    sync_schema_props_perms((rdef.subject, rdef.rtype, rdef.object), syncprops=False)
