import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, Float, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags, json_test


class MobyTag_Provenance_ProvenanceZoneIdentification_MobyTag(Base):
    __tablename__ = "MobyTag_Provenance_ProvenanceZoneIdentification_MobyTag"

    id_tag = Column("MobyTag_Id", UUID, ForeignKey("MobyTag.MobyTag_Id"), primary_key=True, nullable=False)
    id_zone_identification = Column("ProvenanceZoneIdentification_Id", UUID, ForeignKey("ProvenanceZoneIdentification.ProvenanceZoneIdentification_Id"), primary_key=True, nullable=False)

    from ..moby.tag.mobytag import MobyTag
    tag = relationship(MobyTag)

    @property
    def tag_name(self):
        return self.tag.tag

class ProvenanceZoneIdentification(Base):
    # définition de table
    __tablename__ = "ProvenanceZoneIdentification"

    id = Column("ProvenanceZoneIdentification_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    lieu = Column("ProvenanceZoneIdentification_Lieu", String(50), nullable=False)
    from ..reference.qualificatif_lieu import QualificatifLieu as t_qualificatif_lieu
    id_qualificatif_lieu = Column("ProvenanceZoneIdentification_QualificatifLieu_Id", UUID, ForeignKey(t_qualificatif_lieu.id), nullable=True)
    from ..reference.type_site import TypeSite as t_type_site
    id_type_site = Column("ProvenanceZoneIdentification_TypeSite_Id", UUID, ForeignKey(t_type_site.id), nullable=True)
    from ..reference.statut_collecte import StatutCollecte as t_statut_collecte
    id_statut_collecte = Column("ProvenanceZoneIdentification_StatutCollecte_Id", UUID, ForeignKey(t_statut_collecte.id), nullable=True)
    notes = Column("ProvenanceZoneIdentification_Notes", String, nullable=True)
    id_provenance = Column("ProvenanceZoneIdentification_ProvenanceFichier_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    latitude = Column("ProvenanceZoneIdentification_Latitude", Float, nullable=True)
    longitude = Column("ProvenanceZoneIdentification_Longitude", Float, nullable=True)

    #
    #
    #

    provenance_obj = relationship("Provenance", foreign_keys=[id_provenance])
    tags = relationship(MobyTag_Provenance_ProvenanceZoneIdentification_MobyTag)
    qualificatif_lieu = relationship(t_qualificatif_lieu, foreign_keys=[id_qualificatif_lieu])
    type_site = relationship(t_type_site, foreign_keys=[id_type_site])
    statut_collecte = relationship(t_statut_collecte, foreign_keys=[id_statut_collecte])

    #
    #
    #
    
    from .champs.zone_identification.autres_coordonnees import ChampProvenanceZoneIdentificationAutresCoordonnees as t_autres_coordonnees
    autres_coordonnees = relationship(t_autres_coordonnees, back_populates='zone_identification', order_by=t_autres_coordonnees.ordre)

    #
    #
    #

    @property
    def label(self):
        return self.qualificatif_lieu

    @property
    def tags_list(self):
        tl = []
        for t in self.tags:
            tl.append(t.tag_name)
        return tl

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['tags'] = json_tags(self.tags)
        data['lieu'] = self.lieu
        data['qualificatif_lieu'] = json_test(self.qualificatif_lieu)
        data['latitude'] = self.latitude
        data['longitude'] = self.longitude
        data['autres_coordonnees'] = json_loop(self.autres_coordonnees)
        data['type_site'] = json_test(self.type_site)
        data['statut_collecte'] = json_test(self.statut_collecte)
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
