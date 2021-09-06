import uuid
from pathlib import Path, PureWindowsPath

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship, object_session

import logging

from ..base import UUID, Base, indent, json_test
from .zone_generale import MultimediaZoneGenerale

log = logging.getLogger(__name__)


class Multimedia(Base):
    # définitions de table
    __tablename__ = "Multimedia"

    id = Column("Multimedia_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_generale = Column("Multimedia_ZoneGenerale_Id", UUID, ForeignKey("MultimediaZoneGenerale.MultimediaZoneGenerale_Id"), nullable=False)
    id_zone_donnees_techniques = Column("Multimedia_ZoneDonneesTechniques_Id", UUID, nullable=True)
    id_zone_donnees_administratives = Column("Multimedia_ZoneDonneesAdministratives_Id", UUID, nullable=True)
    id_zone_informations_systeme = Column("Multimedia_ZoneInformationsSysteme_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False, server_default=text("DEFAULT"))

    # liaisons

    zone_generale = relationship(MultimediaZoneGenerale, foreign_keys=[id_zone_generale])

    def __init__(self, *args, **kwargs):
        self.t_write_user = text("(USER)")
        self.t_creation_user = text("(USER)")
        super().__init__(*args, **kwargs)
 
    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        
        data['zone_generale'] = json_test(self.zone_generale)
        data['id_zone_donnees_techniques'] = self.id_zone_donnees_techniques
        data['id_zone_donnees_administratives'] = self.id_zone_donnees_administratives
        data['id_zone_informations_systeme'] = self.id_zone_informations_systeme

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()
        
        return data

    #==========================================================================
    #
    # actions
    #

    @property
    def path(self):
        if self.zone_generale:
            return PureWindowsPath(self.zone_generale.chemin).joinpath(self.zone_generale.nom_fichier)
        else:
            log.info("Problem accessing zone_generale id = %s"%(self.id_zone_generale))
            return None

    def updatePath(self, new_path):
        """
        Updates the chemin and nom_fichier attributes in the zone_generale

        returns True if all is in order, False otherwise
        """
        if self.zone_generale:
            return self.zone_generale.updatePath(new_path)
        