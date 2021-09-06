import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_test
from ..reference.type_information import TypeInformation


class SpecimenZoneDescriptionPhysique(Base):
    # définition de table
    __tablename__ = "SpecimenZoneDescriptionPhysique"

    id = Column("SpecimenZoneDescriptionPhysique_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_specimen = Column("SpecimenZoneDescriptionPhysique_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    sexe = Column("SpecimenZoneDescriptionPhysique_Sexe", String(20), nullable=True)
    notes = Column("SpecimenZoneDescriptionPhysique_Notes", String, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # 
    # relationships
    #

    specimen = relationship("Specimen", foreign_keys=[id_specimen])

    from .champs.zone_description_physique.caracteristiques_physiques import ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques as t_caracteristiques_physiques
    caracteristiques_physiques = relationship(t_caracteristiques_physiques,
        order_by=t_caracteristiques_physiques.ordre,
        back_populates='zone_description_physique')
    #
    # object properties
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        
        data['caracteristiques_physiques'] = json_loop(self.caracteristiques_physiques)

        data['sexe'] = self.sexe
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data

