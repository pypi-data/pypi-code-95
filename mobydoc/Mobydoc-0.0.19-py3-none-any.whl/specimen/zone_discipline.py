import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop

class SpecimenZoneDiscipline(Base):
    # définition de table
    __tablename__ = "SpecimenZoneDiscipline"

    id = Column("SpecimenZoneDiscipline_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    from .champs.discipline import ChampDiscipline as t_discipline
    disciplines = relationship(t_discipline, order_by="ChampDiscipline.ordre")

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['disciplines'] = json_loop(self.disciplines)

        return data
