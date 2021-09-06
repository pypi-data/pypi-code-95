import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship


from ...base import UUID, Base, indent, json_test
from ...reference.discipline import Discipline

class ChampDiscipline(Base):
    # définition de table
    __tablename__ = "ChampDiscipline"

    id = Column("ChampDiscipline_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_specimen = Column("ChampDiscipline_Specimen_Id", UUID, ForeignKey("SpecimenZoneDiscipline.SpecimenZoneDiscipline_Id"), nullable=True)
    id_discipline = Column("ChampDiscipline_Discipline_Id", UUID, ForeignKey("Discipline.Reference_Id"), nullable=True)
    ordre = Column("ChampDiscipline_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    discipline = relationship(Discipline, foreign_keys=[id_discipline])
    zone_discipline = relationship("SpecimenZoneDiscipline", foreign_keys=[id_specimen], back_populates="disciplines")

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['discipline'] = json_test(self.discipline)
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data


    @property
    def xml(self):
        s = "<%s id=\"%s\""%(self.__class__.__name__, self.id)
        if self.ordre:
            s+= " ordre=\"%d\""%(self.ordre)
        s+= ">\n"
        if self.discipline:
            s+= indent(self.discipline.xml)
        s+= "</%s>\n"%(self.__class__.__name__)
        return s