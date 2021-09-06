import logging
import uuid
from pathlib import Path, WindowsPath

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base

log = logging.getLogger(__name__)

class MultimediaZoneGenerale(Base):
    __tablename__ = "MultimediaZoneGenerale"

    id = Column("MultimediaZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    reference = Column("MultimediaZoneGenerale_Reference", String(200), nullable=True)
    nom_fichier = Column("MultimediaZoneGenerale_NomFichier", String(255), nullable=True)
    chemin = Column("MultimediaZoneGenerale_Chemin", String(255), nullable=False)
    media = Column("MultimediaZoneGenerale_Media", VARBINARY, nullable=True)
    media_file_name = Column("MultimediaZoneGenerale_Media_FileName", String(256), nullable=True)
    media_content_type = Column("MultimediaZoneGenerale_Media_ContentType", String(128), nullable=True)
    media_attributes = Column("MultimediaZoneGenerale_Media_Attributes", INTEGER, nullable=True)
    media_size = Column("MultimediaZoneGenerale_Media_Size", BIGINT, nullable=True)
    media_last_write = Column("MultimediaZoneGenerale_Media_LastWriteTimeUtc", DATETIME, nullable=True)
    media_last_access = Column("MultimediaZoneGenerale_Media_LastAccessTimeUtc", DATETIME, nullable=True)
    media_creation = Column("MultimediaZoneGenerale_Media_CreationTimeUtc", DATETIME, nullable=True)
    # lien vers la table Designation (non utilisée)
    id_titre = Column("MultimediaZoneGenerale_Titre_Id", UUID, nullable=True)
    notes = Column("MultimediaZoneGenerale_Notes", String, nullable=True)
    # pointe Multimedia.id
    id_multimedia = Column("MultimediaZoneGenerale_MultimediaFichier_Id", UUID, ForeignKey("Multimedia.Multimedia_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    multimedia_obj = relationship("Multimedia", foreign_keys=[id_multimedia])

    def __init__(self, *args, **kwargs):
        self.t_write_user = text("(USER)")
        self.t_creation_user = text("(USER)")
        super().__init__(*args, **kwargs)


    # 
    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        
        data['reference'] = self.reference
        data['nom_fichier'] = self.nom_fichier
        data['chemin'] = self.chemin

        data['media_creation'] = self.media_creation

        data['id_titre'] = self.id_titre
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        return data

    #==========================================================================
    #
    # actions
    #

    def updatePath(self, new_path):
        """
        Updates the chemin and nom_fichier attributes in the zone_generale

        returns True if all is in order, False otherwise
        """
        changed = False

        path = str(new_path.parent)
        if self.chemin != path:
            if path[-1:] != '\\':
                log.info("adding a '\\' at the end of the path '%s'"%(path))
                path+='\\'
            self.chemin = path
            changed = True
        
        name = new_path.name
        if self.nom_fichier != name:
            self.nom_fichier = name
            changed = True
        
        if changed:
            log.info('path changed') 
            self.t_write = text("(getdate())")

        log.info("INFO: %s new path '%s' '%s'"%(self.__class__.__name__, self.chemin, self.nom_fichier))
        return True
