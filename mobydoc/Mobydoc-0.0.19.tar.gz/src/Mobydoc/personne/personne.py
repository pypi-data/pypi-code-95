import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test

class Personne(Base):
    __tablename__ = "Personne"

    id = Column("Personne_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_identification = Column("Personne_ZoneIdentification_Id", UUID, ForeignKey("PersonneZoneIdentification.PersonneZoneIdentification_Id"), nullable=False)
    id_zone_donnees_biographiques = Column("Personne_ZoneDonneesBiographiques_Id", UUID, nullable=True)
    id_zone_droit_moral = Column("Personne_ZoneDroitMoral_Id", UUID, nullable=True)
    id_zone_p_adherent = Column("Personne_ZonePAdherent_Id", UUID, nullable=True)
    id_zone_contexte = Column("Personne_ZoneContexte_Id", UUID, nullable=True)
    id_zone_informations_systeme = Column("Personne_ZoneInformationsSysteme_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons
    from .zone_identification import PersonneZoneIdentification as t_zone_identification
    zone_identification = relationship(t_zone_identification, foreign_keys=[id_zone_identification])

    @property
    def nom_entier(self):
        return self.zone_identification.nom_entier

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_identification'] = json_test(self.zone_identification)
        data['id_zone_donnees_biographiques'] = self.id_zone_donnees_biographiques
        data['id_zone_droit_moral'] = self.id_zone_droit_moral
        data['id_zone_p_adherent'] = self.id_zone_p_adherent
        data['id_zone_contexte'] = self.id_zone_contexte
        data['id_zone_informations_systeme'] = self.id_zone_informations_systeme

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data        
