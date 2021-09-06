import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test

class DatationZoneGenerale(Base):
    __tablename__ = "DatationZoneGenerale"

    id = Column("DatationZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    datation = Column("DatationZoneGenerale_Datation", String(256), nullable=True)
    id_borne_inferieure = Column("DatationZoneGenerale_BorneInferieure_Id", UUID, ForeignKey("MobyChampDate.MobyChampDate_Id"), nullable=True)
    id_borne_superieure = Column("DatationZoneGenerale_BorneSuperieure_Id", UUID, ForeignKey("MobyChampDate.MobyChampDate_Id"), nullable=True)
    notes = Column("DatationZoneGenerale_Notes", String, nullable=True)
    id_datation_fichier = Column("DatationZoneGenerale_DatationFichier_Id", UUID, ForeignKey("Datation.Datation_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    from ..moby.champ.date import MobyChampDate as t_date
    borne_inferieure = relationship(t_date, foreign_keys=[id_borne_inferieure])
    borne_superieure = relationship(t_date, foreign_keys=[id_borne_superieure])
    l_datation = relationship("Datation", foreign_keys=[id_datation_fichier])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['datation'] = self.datation
        data['borne_inferieure'] = json_test(self.borne_inferieure)
        data['borne_superieure'] = json_test(self.borne_superieure)
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data