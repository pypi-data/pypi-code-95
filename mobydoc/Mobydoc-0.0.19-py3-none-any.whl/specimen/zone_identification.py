import re
import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags


class MobyTag_Specimen_SpecimenZoneIdentification_MobyTag(Base):
    __tablename__ = "MobyTag_Specimen_SpecimenZoneIdentification_MobyTag"

    id_tag = Column("MobyTag_Id", UUID, ForeignKey("MobyTag.MobyTag_Id"), primary_key=True, nullable=False)
    id_zone_identification = Column("SpecimenZoneIdentification_Id", UUID, ForeignKey("SpecimenZoneIdentification.SpecimenZoneIdentification_Id"), primary_key=True, nullable=False)

    from ..moby.tag.mobytag import MobyTag
    tag = relationship(MobyTag)

class SpecimenZoneIdentification(Base):
    # définition de table
    __tablename__ = "SpecimenZoneIdentification"

    id = Column("SpecimenZoneIdentification_Id", UUID, ForeignKey("Specimen.Specimen_ZoneIdentification_Id"), primary_key=True, nullable=False, default=uuid.uuid4)

    numero_inventaire = Column("SpecimenZoneIdentification_NumeroInventaire", String(200), nullable=True)
    numero_depot = Column("SpecimenZoneIdentification_NumeroDepot", String(200), nullable=True)
    numero_inventaire_deposant = Column("SpecimenZoneIdentification_NumeroInventaireDeposant", String(200), nullable=True)
    id_date_inscription_registre_inventaire = Column("SpecimenZoneIdentification_DateInscriptionRegistreInventaire_Id", UUID, nullable=True)
    nombre_parties = Column("SpecimenZoneIdentification_NombreParties", INTEGER, nullable=True)
    nombre_specimens = Column("SpecimenZoneIdentification_NombreSpecimens", INTEGER, nullable=True)
    existence_sous_inventaire = Column("SpecimenZoneIdentification_ExistenceSousInventaire", INTEGER, nullable=True)
    observations_reference = Column("SpecimenZoneIdentification_ObservationsReference", String, nullable=True)
    notes = Column("SpecimenZoneIdentification_Notes", String, nullable=True)
    moby_cle = Column("SpecimenZoneIdentification_MobyCle", String(201), nullable=True)
    
    id_specimen = Column("SpecimenZoneIdentification_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons
    specimen = relationship("Specimen", foreign_keys=[id_specimen])
    
    from .champs.zone_identification.autre_numero import ChampSpecimenAutreNumero as t_autre_numero
    autres_numeros = relationship(t_autre_numero, order_by=t_autre_numero.ordre)
    tags = relationship("MobyTag_Specimen_SpecimenZoneIdentification_MobyTag")

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
         
        data['numero_inventaire'] = self.numero_inventaire
        data['numero_depot'] = self.numero_depot
        data['numero_inventaire_deposant'] = self.numero_inventaire_deposant
        data['date_inscription_registre_inventaire'] = self.id_date_inscription_registre_inventaire # TODO
        data['autres_numeros'] = json_loop(self.autres_numeros)
        data['nombre_parties'] = self.nombre_parties
        data['nombre_specimens'] = self.nombre_specimens
        data['existence_sous_inventaire'] = self.existence_sous_inventaire
        data['observations_reference'] = self.observations_reference
        data['notes'] = self.notes
        data['moby_cle'] = self.moby_cle    
        data['tags'] = json_tags(self.tags)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
