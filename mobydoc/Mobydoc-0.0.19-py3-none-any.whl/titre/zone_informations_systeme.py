import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent

class TitreZoneInformationsSysteme(Base):
    # définition de table
    __tablename__ = "TitreZoneInformationsSysteme"

    id = Column("TitreZoneInformationsSysteme_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_titre = Column("TitreZoneInformationsSysteme_TitreFichier_Id", UUID, ForeignKey("Titre.Titre_Id"), nullable=True)
    creation_time = Column("TitreZoneInformationsSysteme_CreationTime", DateTime, nullable=False)
    creation_user = Column("TitreZoneInformationsSysteme_CreationUser", String(256), nullable=False)
    last_write_time = Column("TitreZoneInformationsSysteme__trackLastWriteTime", DateTime, nullable=False)
    last_write_user = Column("TitreZoneInformationsSysteme_LastWriteUser", String(256), nullable=False)
    statut_notice = Column("TitreZoneInformationsSysteme_StatutNotice", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    titre_obj = relationship("Titre", foreign_keys=[id_titre])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['creation_time'] = self.creation_time.isoformat()
        data['creation_user'] = self.creation_user
        data['last_write_time'] = self.last_write_time.isoformat()
        data['last_write_user'] = self.last_write_user
        data['statut_notice'] = self.statut_notice

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
