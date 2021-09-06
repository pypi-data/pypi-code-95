import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY, Float,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop


class SpecimenZoneCollecte(Base):
    # définition de table
    __tablename__ = "SpecimenZoneCollecte"

    id = Column("SpecimenZoneCollecte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_methode_collecte = Column("SpecimenZoneCollecte_MethodeCollecte_Id", UUID, nullable=True)
    notes = Column("SpecimenZoneCollecte_Notes", String, nullable=True)
    id_specimen = Column("SpecimenZoneCollecte_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    latitude = Column("SpecimenZoneCollecte_Latitude", Float, nullable=True)
    longitude = Column("SpecimenZoneCollecte_Longitude", Float, nullable=True)

    #
    # Links
    # 

    specimen = relationship("Specimen", foreign_keys=[id_specimen])
    
    #
    # external links
    #
    
    from .champs.zone_collecte.provenance import ChampSpecimenZoneCollecteProvenance as t_provenance
    provenances = relationship(t_provenance, back_populates='zone_collecte', order_by=t_provenance.ordre)
    from .champs.zone_collecte.autres_coordonnees import ChampSpecimenZoneCollecteAutresCoordonnees as t_autres_coordonnees
    autres_coordonnees = relationship(t_autres_coordonnees, back_populates='zone_collecte', order_by=t_autres_coordonnees.ordre)

    from .champs.zone_collecte.collecteur import ChampSpecimenZoneCollecteCollecteur as t_collecteur
    collecteurs = relationship(t_collecteur, back_populates='zone_collecte', order_by=t_collecteur.ordre)

    # 
    # generate json representation
    # 

    @property
    def provenance_list(self):
        data = []
        for p in self.provenances:
            data.append(p.tree)
        return data

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['provenances'] = json_loop(self.provenances)
        data['latitude'] = self.latitude
        data['longitude'] = self.longitude
        data['autres_coordonnees'] = json_loop(self.autres_coordonnees)

        # biotope

        # collecteur

        # date de collecte

        data['id_methode_collecte'] = self.id_methode_collecte
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data