import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship


from ....base import UUID, Base, indent, json_test

class ChampSpecimenZoneDeterminationDeterminateur(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDeterminationDeterminateur"

    id = Column("ChampSpecimenZoneDeterminationDeterminateur_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_determination = Column("ChampSpecimenZoneDeterminationDeterminateur_SpecimenZoneDetermination_Id", UUID, ForeignKey("SpecimenZoneDetermination.SpecimenZoneDetermination_Id"), nullable=True)
    id_determinateur = Column("ChampSpecimenZoneDeterminationDeterminateur_Determinateur_Id", UUID, ForeignKey("Personne.Personne_Id"), nullable=True)
    ordre = Column("ChampSpecimenZoneDeterminationDeterminateur_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons 
    zone_determination = relationship("SpecimenZoneDetermination", foreign_keys=[id_zone_determination], post_update=True, back_populates="determinateurs")
    from ....personne.personne import Personne as t_personne
    personne = relationship(t_personne, foreign_keys=[id_determinateur], post_update=True)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['determinateur'] = json_test(self.personne)
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
