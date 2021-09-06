import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text, Integer
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import relationship

from ...base import UUID, Base, indent

class MobyChampDate(Base):
    __tablename__ = "MobyChampDate"

    id = Column("MobyChampDate_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    jour = Column("MobyChampDate_Jour", TINYINT, nullable=True)
    mois = Column("MobyChampDate_Mois", TINYINT, nullable=True)
    annee = Column("MobyChampDate_Année", Integer, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)


    def isoformat(self):
        if self.jour and self.mois and self.annee:
            return ('%04d-%02d-%02d'%(self.annee, self.mois, self.jour))
        return None

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['jour'] = self.jour
        data['mois'] = self.mois
        data['annee'] = self.annee

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
