import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test

#
# in this one there is no 's' at Autre 
# 


class ChampProvenanceZoneIdentificationAutresCoordonnees(Base):
    # définition de table
    __tablename__ = "ChampProvenanceZoneIdentificationAutreCoordonnees"

    id = Column("ChampProvenanceZoneIdentificationAutreCoordonnees_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_identification = Column("ChampProvenanceZoneIdentificationAutreCoordonnees_ProvenanceZoneIdentification_Id", UUID, ForeignKey("ProvenanceZoneIdentification.ProvenanceZoneIdentification_Id"), nullable=True)
    from ....reference.coordonnees import Coordonnees as t_coordonnees
    id_autre_coordonnee = Column("ChampProvenanceZoneIdentificationAutreCoordonnees_AutresCoordonnees_Id", UUID, ForeignKey(t_coordonnees.id), nullable=True)
    valeur = Column("ChampProvenanceZoneIdentificationAutreCoordonnees_Valeur", String(256), nullable=True)
    ordre = Column("ChampProvenanceZoneIdentificationAutreCoordonnees_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    zone_identification = relationship("ProvenanceZoneIdentification", foreign_keys=[id_zone_identification])
    autre_coordonnee = relationship(t_coordonnees)

    #
    # external links
    #

    # 
    # generate json representation
    # 

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['autres_coordonnees'] = json_test(self.autre_coordonnee)
        data['valeur'] = self.valeur

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data