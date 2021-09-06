import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship, backref

from ..base import UUID, Base, indent, json_loop, json_test

class LocalisationZoneGenerale(Base):
    __tablename__ = "LocalisationZoneGenerale"

    id = Column("LocalisationZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    localisation = Column("LocalisationZoneGenerale_Localisation", String(200), nullable=True)
    id_type_localisation = Column("LocalisationZoneGenerale_TypeLocalisation_Id", UUID, nullable=True)
    id_numero_marquage = Column("LocalisationZoneGenerale_NumeroMarquage_Id", UUID, nullable=True)
    id_adresse = Column("LocalisationZoneGenerale_Adresse_Id", UUID, nullable=True)
    notes = Column("LocalisationZoneGenerale_Notes", String, nullable=True)
    id_localisation = Column("LocalisationZoneGenerale_LocalisationFichier_Id", UUID, 
        ForeignKey("Localisation.Localisation_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    # from .zone_generale import DatationZoneGenerale as t_zone_generale
    # zone_generale = relationship(t_zone_generale, foreign_keys=[id_zone_generale])
    from .champ.zone_generale.multimedia import ChampLocalisationZoneGeneraleMultimedia as t_champ_multimedia
    multimedias = relationship(t_champ_multimedia)

    localisation_obj = relationship("Localisation", foreign_keys=[id_localisation], 
        backref=backref('Localisation', remote_side=id_localisation))

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['localisation'] = self.localisation
        data['id_type_localisation'] = self.id_type_localisation
        data['id_numero_marquage'] = self.id_numero_marquage
        
        data['id_adresse'] = self.id_adresse
        data['multimedias'] = json_loop(self.multimedias)
        data['notes'] = self.notes
        

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
