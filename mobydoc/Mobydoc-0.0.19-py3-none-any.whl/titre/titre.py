import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test

class Titre(Base):
    # définition de table
    __tablename__ = "Titre"

    id = Column("Titre_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    from .zone_generale import TitreZoneGenerale as t_zone_generale
    id_zone_generale = Column("Titre_ZoneGenerale_Id", UUID, ForeignKey(t_zone_generale.id), nullable=False)
    from .zone_contexte import TitreZoneContexte as t_zone_contexte
    id_zone_contexte = Column("Titre_ZoneContexte_Id", UUID, ForeignKey(t_zone_contexte.id), nullable=True)
    from .zone_informations_systeme import TitreZoneInformationsSysteme as t_zone_informations_systeme
    id_zone_informations_systeme = Column("Titre_ZoneInformationsSysteme_Id", UUID, ForeignKey(t_zone_informations_systeme.id), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    #
    #

    zone_generale = relationship(t_zone_generale, foreign_keys=[id_zone_generale])
    zone_contexte = relationship(t_zone_contexte, foreign_keys=[id_zone_contexte])
    zone_informations_systeme = relationship(t_zone_informations_systeme, foreign_keys=[id_zone_informations_systeme])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_generale'] = json_test(self.zone_generale)
        data['zone_informations_systeme'] = json_test(self.zone_informations_systeme)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
