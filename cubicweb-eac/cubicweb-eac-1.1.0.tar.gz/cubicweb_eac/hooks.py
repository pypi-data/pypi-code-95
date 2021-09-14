# copyright 2016-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-eac specific hooks and operations"""

from cubicweb import (
    _,
    ValidationError,
)
from cubicweb.predicates import is_instance
from cubicweb.server import hook


class DeleteTernaryRelationsHook(hook.Hook):
    """When an AuthorityRecord entity is being deleted we need to delete all
    "qualified" (ternary) relations with another AuthorityRecord, otherwise
    we'll get a validation error about one side of the ternary relation being
    missing.
    """

    __select__ = hook.Hook.__select__ & is_instance("AuthorityRecord")
    __regid__ = "eac.delete-ternary-relations"
    events = ("before_delete_entity",)

    def __call__(self):
        errors, msgargs = {}, {}
        for rtype in (
            "association_from",
            "association_to",
            "chronological_predecessor",
            "chronological_successor",
            "hierarchical_parent",
            "hierarchical_child",
            "family_from",
            "family_to",
            "identity_from",
            "identity_to",
        ):
            for relation in self.entity.related(rtype, role="object").entities():
                if self._cw.deleted_in_transaction(relation.eid):
                    continue
                if relation.cw_has_perm("delete"):
                    self.info(
                        'deleting "%s" as %s-object is being deleted',
                        relation.dc_title(),
                        rtype,
                    )
                    relation.cw_delete()
                else:
                    argname = "{}-subject-{}".format(rtype, relation.eid)
                    errors[rtype] = _(
                        '"%({})s" would need to be deleted alongside '
                        "the AuthorityRecord but this is disallowed"
                    ).format(argname)
                    msgargs[argname] = relation.dc_title()
        if errors:
            raise ValidationError(self.entity.eid, errors, msgargs)


# ensure that equivalent_concept Concept has vocabulary_source defined ####################


class EnsureVocabularySource(hook.Hook):
    """When a equivalent_concept relation is set and targets a Concept, ensure that the
    vocabulary_source relation is set to the concept's scheme. This should not be necessary when
    using the UI where the workflow enforce setting the scheme first, but it's necessary during
    e.g. EAC import.
    """

    __select__ = hook.Hook.__select__ & hook.match_rtype(
        "equivalent_concept", toetypes=("Concept",)
    )
    __regid__ = "eac.add_equivalent_concept"
    events = ("after_add_relation",)

    def __call__(self):
        EnsureVocabularySourceOp.get_instance(self._cw).add_data(
            (self.eidfrom, self.eidto)
        )


class EnsureVocabularySourceOp(hook.DataOperationMixIn, hook.Operation):
    """Ensure X equivalent_concept target Concept as proper X vocabulary_source Scheme"""

    def precommit_event(self):
        cnx = self.cnx
        for eid, concept_eid in self.get_data():
            cnx.execute(
                "SET X vocabulary_source SC WHERE NOT X vocabulary_source SC, "
                "C in_scheme SC, C eid %(c)s, X eid %(x)s",
                {"x": eid, "c": concept_eid},
            )


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)

    # Add relations involved in a composite graph with security setup to "on
    # commit" check step.
    from cubicweb.server import ON_COMMIT_ADD_RELATIONS
    from cubicweb_compound.utils import mandatory_rdefs
    from cubicweb_eac import AuthorityRecordGraph

    graph = AuthorityRecordGraph(vreg.schema)
    for rdef, __ in mandatory_rdefs(
        vreg.schema, graph.parent_structure("AuthorityRecord")
    ):
        ON_COMMIT_ADD_RELATIONS.add(rdef.rtype)
