import uuid

from sqlalchemy import (TIMESTAMP, Column, DateTime, ForeignKey, String,
                        column, func, select, text)
from sqlalchemy.orm import column_property, relationship

from ..base import UUID, Base, indent, json_test


class CaracteristiquesPhysiques(Base):
    __tablename__ = "CaracteristiquesPhysiques"

    id = Column("CaracteristiquesPhysiques_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    # ClassificationZoneIdentification.ClassificationZoneIdentification_Id
    from .zone_generale import CaracteristiquesPhysiquesZoneGenerale as t_zone_generale
    id_zone_generale = Column("CaracteristiquesPhysiques_ZoneGenerale_Id", UUID, ForeignKey(t_zone_generale.id), nullable=False)
    id_zone_contexte = Column("CaracteristiquesPhysiques_ZoneContexte_Id", UUID, nullable=True)
    id_zone_informations_systeme = Column("CaracteristiquesPhysiques_ZoneInformationsSysteme_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # 
    # liaisons
    #

    #from .zone_generale import CaracteristiquesPhysiquesZoneGenerale as t_zone_generale
    zone_generale = relationship(t_zone_generale, foreign_keys=[id_zone_generale])
    # from .zone_contexte import CaracteristiquesPhysiquesZoneContexte as t_zone_contexte
    # zone_contexte = relationship(t_zone_contexte, foreign_keys=[id_zone_contexte])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_generale'] = json_test(self.zone_generale)
        data['id_zone_contexte'] = self.id_zone_contexte
        data['id_zone_informations_systeme'] = self.id_zone_informations_systeme

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
