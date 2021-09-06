import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent

class TitreZoneGenerale(Base):
    # définition de table
    __tablename__ = "TitreZoneGenerale"

    id = Column("TitreZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    titre = Column("TitreZoneGenerale_Titre", String(500), nullable=False)
    complement_titre = Column("TitreZoneGenerale_ComplementTitre", String, nullable=True)
    id_titre = Column("TitreZoneGenerale_TitreFichier_Id", UUID, ForeignKey("Titre.Titre_Id"), nullable=True)

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

        data['titre'] = self.titre
        data['complement_titre'] = self.complement_titre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
