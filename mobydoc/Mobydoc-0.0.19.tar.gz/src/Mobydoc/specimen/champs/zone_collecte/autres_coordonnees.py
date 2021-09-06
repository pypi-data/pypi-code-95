import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneCollecteAutresCoordonnees(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneCollecteAutresCoordonnees"

    id = Column("ChampSpecimenZoneCollecteAutresCoordonnees_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_collecte = Column("ChampSpecimenZoneCollecteAutresCoordonnees_SpecimenZoneCollecte_Id", UUID, ForeignKey("SpecimenZoneCollecte.SpecimenZoneCollecte_Id"), nullable=True)
    from ....reference.coordonnees import Coordonnees as t_coordonnees
    id_autre_coordonnee = Column("ChampSpecimenZoneCollecteAutresCoordonnees_AutresCoordonnees_Id", UUID, ForeignKey(t_coordonnees.id), nullable=True)
    valeur = Column("ChampSpecimenZoneCollecteAutresCoordonnees_Valeur", String(256), nullable=True)
    ordre = Column("ChampSpecimenZoneCollecteAutresCoordonnees_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    zone_collecte = relationship("SpecimenZoneCollecte", foreign_keys=[id_zone_collecte], back_populates='autres_coordonnees')
    autre_coordonnee = relationship(t_coordonnees)

    #
    # external links
    #

    # 
    # generate json representation
    # 

    @property
    def label(self):
        return self.autre_coordonnee.label if self.autre_coordonnee else None
        
    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['autre_coordonnee'] = json_test(self.autre_coordonnee)
        data['valeur'] = self.valeur

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data