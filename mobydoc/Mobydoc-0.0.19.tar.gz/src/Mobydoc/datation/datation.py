import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test

class Datation(Base):
    __tablename__ = "Datation"

    id = Column("Datation_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_generale = Column("Datation_ZoneGenerale_Id", UUID, ForeignKey("DatationZoneGenerale.DatationZoneGenerale_Id"), nullable=False)
    id_zone_contexte = Column("Datation_ZoneContexte_Id", UUID, nullable=True)
    id_zone_informations_systeme = Column("Datation_ZoneInformationsSysteme_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons
    from .zone_generale import DatationZoneGenerale as t_zone_generale
    zone_generale = relationship(t_zone_generale, foreign_keys=[id_zone_generale])

    def __str__(self):
        if self.zone_generale:
            if self.zone_generale.datation:
                return self.zone_generale.datation
            b_inf = self.zone_generale.borne_inferieure
            b_sup = self.zone_generale.borne_superieure
            if b_inf and b_sup:
                pass
            elif b_inf:
                pass
            elif b_sup:
                pass
        return "(datation invalide)"

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