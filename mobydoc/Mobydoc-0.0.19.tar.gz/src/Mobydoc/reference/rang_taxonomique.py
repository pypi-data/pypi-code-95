import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test
from .reference import Reference

class RangTaxonomique(Base):
    # table definitions
    __tablename__ = "RangTaxonomique"

    id = Column("Reference_Id", UUID, ForeignKey("Reference.Reference_Id"), primary_key=True, nullable=False, default=uuid.uuid4)
    id_zone_contexte = Column("RangTaxonomique_ZoneContexte_Id", UUID, ForeignKey("RangTaxonomiqueZoneContexte.RangTaxonomiqueZoneContexte_Id"), nullable=True)

    # liaisons
    reference = relationship(Reference, foreign_keys=[id])
    zone_contexte = relationship("RangTaxonomiqueZoneContexte", foreign_keys=[id_zone_contexte], post_update=True)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['reference'] = json_test(self.reference)
        data['zone_contexte'] = json_test(self.zone_contexte)

        return data

class RangTaxonomiqueZoneContexte(Base):
    __tablename__ = "RangTaxonomiqueZoneContexte"

    id = Column("RangTaxonomiqueZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    
    id_rang_taxonomique_fichier = Column("RangTaxonomiqueZoneContexte_RangTaxonomiqueFichier_Id", UUID, nullable=True)
    id_parent = Column("RangTaxonomiqueZoneContexte_Parent_Id", UUID, nullable=True)
    id_voir = Column("RangTaxonomiqueZoneContexte_Voir_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['id_parent'] = self.id_parent
        data['id_voir'] = self.id_voir

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
