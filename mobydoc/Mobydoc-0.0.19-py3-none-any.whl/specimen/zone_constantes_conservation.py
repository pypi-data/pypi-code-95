import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_test


class SpecimenZoneConstantesConservation(Base):
    # définition de table
    __tablename__ = "SpecimenZoneConstantesConservation"

    id = Column("SpecimenZoneConstantesConservation_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_specimen = Column("SpecimenZoneConstantesConservation_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    statut_specimen = Column("SpecimenZoneConstantesConservation_StatutSpecimenConstantesConservation", INTEGER, nullable=True)

    from ..localisation.localisation import Localisation as t_localisation
    id_localisation_permanente = Column("SpecimenZoneConstantesConservation_LocalisationPermanente_Id", UUID, ForeignKey(t_localisation.id), nullable=True)

    id_unite_conditionnement = Column("SpecimenZoneConstantesConservation_UniteConditionnement_Id", UUID, ForeignKey(t_localisation.id), nullable=True)

    from ..reference.situation import Situation as t_situation
    id_situation = Column("SpecimenZoneConstantesConservation_Situation_Id", UUID, ForeignKey(t_situation.id), nullable=True)

    from ..moby.champ.date import MobyChampDate as t_champ_date
    id_date_localisation = Column("SpecimenZoneConstantesConservation_DateLocalisation_Id", UUID, ForeignKey(t_champ_date.id), nullable=True)
    
    autorisation_necessaire = Column("SpecimenZoneConstantesConservation_AutorisationNecessaire", String, nullable=True)
    notes = Column("SpecimenZoneConstantesConservation_Notes", String, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    specimen = relationship("Specimen", foreign_keys=[id_specimen])
    localisation_permanente = relationship(t_localisation, foreign_keys=[id_localisation_permanente])
    unite_conditionnement = relationship(t_localisation, foreign_keys=[id_unite_conditionnement])

    situation = relationship(t_situation, foreign_keys=[id_situation])
    date_localisation = relationship(t_champ_date, foreign_keys=[id_date_localisation])
    
    #
    # external links
    #

    from .champs.zone_constantes_conservation.conditions_pret import ChampSpecimenConstantesConservationConditionsPret as t_conditions_pret
    conditions_pret = relationship(t_conditions_pret)

    # 
    # generate json representation
    # 

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['statut_specimen'] = self.statut_specimen
        data['localisation_permanente'] = json_test(self.localisation_permanente)
        data['unite_conditionnement'] = json_test(self.unite_conditionnement)
        data['situation'] = json_test(self.situation)
        data['date_localisation'] = json_test(self.date_localisation)
        data['conditions_pret'] = json_loop(self.conditions_pret)
        data['autorisation_necessaire'] = self.autorisation_necessaire
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data

    @property
    def localisation(self):
        if self.localisation_permanente:
            return self.localisation_permanente.localisation
        return None