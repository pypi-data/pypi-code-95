import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY, Float,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop


class SpecimenZoneDatationGeologique(Base):
    # définition de table
    __tablename__ = "SpecimenZoneDatationGeologique"

    id = Column("SpecimenZoneDatationGeologique_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    notes = Column("SpecimenZoneDatationGeologique_Notes", String, nullable=True)
    id_specimen = Column("SpecimenZoneDatationGeologique_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    specimen = relationship("Specimen", foreign_keys=[id_specimen])
    
    #
    # external links
    #
    
    # datation_geologique
    from .champs.zone_datation_geologique.datation_geologique import ChampSpecimenZoneDatationGeologiqueDatationGeologique as t_datation_geologique
    datations_geologiques = relationship(t_datation_geologique, back_populates='zone_datation_geologique', order_by=t_datation_geologique.ordre)
    # référence bibliographique
    # from .champs.zone_collecte.autres_coordonnees import ChampSpecimenZoneCollecteAutresCoordonnees as t_autres_coordonnees
    # autres_coordonnees = relationship(t_autres_coordonnees, back_populates='zone_collecte', order_by=t_autres_coordonnees.ordre)

    # 
    # generate json representation
    # 

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['datations_geologiques'] = json_loop(self.datations_geologiques)
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data