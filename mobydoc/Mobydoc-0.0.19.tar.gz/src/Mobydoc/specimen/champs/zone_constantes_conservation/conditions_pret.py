import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship


from ....base import UUID, Base, indent, json_test

class ChampSpecimenConstantesConservationConditionsPret(Base):
    # définition de table
    __tablename__ = "ChampSpecimenConstantesConservationConditionsPret"

    id = Column("ChampSpecimenConstantesConservationConditionsPret_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_constantes_conservation = Column("ChampSpecimenConstantesConservationConditionsPret_SpecimenZoneConstantesConservation_Id", UUID, 
        ForeignKey("SpecimenZoneConstantesConservation.SpecimenZoneConstantesConservation_Id"), nullable=True)
    from ....reference.conditions_pret import ConditionsPret as t_conditions_pret
    id_condition_pret = Column("ChampSpecimenConstantesConservationConditionsPret_ConditionsPret_Id", UUID, ForeignKey(t_conditions_pret.id), nullable=True)
    ordre = Column("ChampSpecimenConstantesConservationConditionsPret_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    condition_pret = relationship(t_conditions_pret, foreign_keys=[id_condition_pret], post_update=True)
    zone_constantes_conservation = relationship("SpecimenZoneConstantesConservation", foreign_keys=[id_zone_constantes_conservation])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['condition_pret'] = json_test(self.condition_pret)
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
