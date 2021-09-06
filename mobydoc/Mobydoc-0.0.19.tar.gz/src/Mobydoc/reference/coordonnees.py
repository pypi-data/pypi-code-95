import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test
from .reference import Reference

class CoordonneesZoneContexte(Base):
    __tablename__ = "CoordonneesZoneContexte"

    id = Column("CoordonneesZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    
    id_coordonnees_fichier = Column("CoordonneesZoneContexte_CoordonneesFichier_Id", UUID, nullable=True)
    id_parent = Column("CoordonneesZoneContexte_Parent_Id", UUID, ForeignKey("Coordonnees.Reference_Id"), nullable=True)
    id_voir = Column("CoordonneesZoneContexte_Voir_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    parent = relationship("Coordonnees", foreign_keys=[id_parent])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['parent'] = json_test(self.parent)
        data['id_voir'] = self.id_voir

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data

class Coordonnees(Base):
    # table definitions
    __tablename__ = "Coordonnees"

    id = Column("Reference_Id", UUID, ForeignKey("Reference.Reference_Id"), primary_key=True, nullable=False, default=uuid.uuid4)
    id_zone_contexte = Column("Coordonnees_ZoneContexte_Id", UUID, ForeignKey(CoordonneesZoneContexte.id), nullable=True)

    # liaisons
    reference = relationship(Reference, foreign_keys=[id])
    zone_contexte = relationship(CoordonneesZoneContexte, foreign_keys=[id_zone_contexte], post_update=True)

    @property
    def label(self):
        return self.reference.label if self.reference else None

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['reference'] = json_test(self.reference)
        data['zone_contexte'] = json_test(self.zone_contexte)

        return data
