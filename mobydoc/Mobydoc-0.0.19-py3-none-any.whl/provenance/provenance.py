import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_test


class Provenance(Base):
    # définition de table
    __tablename__ = "Provenance"

    id = Column("Provenance_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    from .zone_identification import ProvenanceZoneIdentification as t_zone_identification
    id_zone_identification = Column("Provenance_ZoneIdentification_Id", UUID, ForeignKey(t_zone_identification.id), nullable=False)

    from .zone_description import ProvenanceZoneDescription as t_zone_description
    id_zone_description = Column("Provenance_ZoneDescription_Id", UUID, ForeignKey(t_zone_description.id), nullable=False)

    from .zone_contexte import ProvenanceZoneContexte as t_zone_contexte
    id_zone_contexte = Column("Provenance_ZoneContexte_Id", UUID, ForeignKey(t_zone_contexte.id), nullable=False)

    from .zone_informations_systeme import ProvenanceZoneInformationsSysteme as t_zone_informations_systeme
    id_zone_informations_systeme = Column("Provenance_ZoneInformationsSysteme_Id", UUID, ForeignKey(t_zone_informations_systeme.id), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    #
    #

    zone_identification = relationship(t_zone_identification, foreign_keys=[id_zone_identification])
    zone_description = relationship(t_zone_description, foreign_keys=[id_zone_description])
    zone_contexte = relationship(t_zone_contexte, foreign_keys=[id_zone_contexte])
    zone_informations_systeme = relationship(t_zone_informations_systeme, foreign_keys=[id_zone_informations_systeme])

    #
    #
    #

    from .zone_bibliographie import ProvenanceZoneBibliographie as t_zone_bibliographie
    zones_bibliographie = relationship(t_zone_bibliographie, order_by=t_zone_bibliographie.ordre)    


    #
    #
    #

    children_zone_contexte = relationship(t_zone_contexte, primaryjoin=id==t_zone_contexte.id_parent)
    
    @property
    def children(self):
        c = []
        for c_zc in self.children_zone_contexte:
            c.append(c_zc.provenance_obj)
        return c
    
    @property
    def types(self):
        zi = self.zone_identification
        if zi:
            return zi.tags_list
        return None
    
    @property
    def tree(self):
        names = []
        if self.zone_contexte and self.zone_contexte.parent_obj:
            names = self.zone_contexte.parent_obj.tree

        data = {}
        if self.zone_identification:
            data['name'] = self.zone_identification.lieu
            data['label'] = self.zone_identification.label
            data['tags'] = self.zone_identification.tags_list
        names.append(data)
        return names

    @property
    def name_tree(self):
        names = []
        if self.zone_contexte and self.zone_contexte.parent_obj:
            names = self.zone_contexte.parent_obj.name_tree
        if self.zone_identification.lieu:
            names.append(self.zone_identification.lieu)
        else:
            names.append("(unknown)")
        return names

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_identification'] = json_test(self.zone_identification)
        data['zone_description'] = json_test(self.zone_description)
        data['zones_bibliographie'] = json_loop(self.zones_bibliographie)
        data['zone_contexte'] = json_test(self.zone_contexte)
        data['zone_informations_systeme'] = json_test(self.zone_informations_systeme)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
