import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship


from ....base import UUID, Base, indent, json_test

class ChampLocalisationZoneGeneraleMultimedia(Base):
    # définition de table
    __tablename__ = "ChampLocalisationZoneGeneraleMultimedia"

    id = Column("ChampLocalisationZoneGeneraleMultimedia_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_generale = Column("ChampLocalisationZoneGeneraleMultimedia_LocalisationZoneGenerale_Id", UUID, ForeignKey("LocalisationZoneGenerale.LocalisationZoneGenerale_Id"), nullable=True)
    from ....multimedia.multimedia import Multimedia as t_multimedia
    id_multimedia = Column("ChampLocalisationZoneGeneraleMultimedia_Multimedia_Id", UUID, ForeignKey(t_multimedia.id), nullable=True)
    ordre = Column("ChampLocalisationZoneGeneraleMultimedia_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    multimedia = relationship(t_multimedia, foreign_keys=[id_multimedia], post_update=True)
    zone_generale = relationship("LocalisationZoneGenerale", foreign_keys=[id_zone_generale])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['multimedia'] = json_test(self.multimedia)
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
