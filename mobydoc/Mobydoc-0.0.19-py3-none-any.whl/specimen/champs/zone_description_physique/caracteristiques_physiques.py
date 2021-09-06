import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques"

    id = Column("ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_description_physique = Column("ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques_SpecimenZoneDescriptionPhysique_Id", \
        UUID, ForeignKey("SpecimenZoneDescriptionPhysique.SpecimenZoneDescriptionPhysique_Id"), nullable=True)

    from ....caracteristiques_physiques.caracteristiques_physiques import CaracteristiquesPhysiques as t_caracteristiques_physiques
    id_caracteristique_physique = Column( 
        "ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques_CaracteristiquesPhysiques_Id", 
        UUID, 
        ForeignKey(t_caracteristiques_physiques.id), 
        nullable=True)
    valeur = Column("ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques_Valeur", INTEGER, nullable=True)
    ordre = Column("ChampSpecimenZoneDescriptionPhysiqueCaracteristiquesPhysiques_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    zone_description_physique = relationship("SpecimenZoneDescriptionPhysique", 
        foreign_keys=[id_zone_description_physique],
        back_populates='caracteristiques_physiques')
    caracteristique_physique = relationship(t_caracteristiques_physiques, foreign_keys=[id_caracteristique_physique])

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

        data['id_caracteristique_physique'] = self.id_caracteristique_physique
        data['caracteristique_physique'] = json_test(self.caracteristique_physique)
        data['valeur'] = self.valeur

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data