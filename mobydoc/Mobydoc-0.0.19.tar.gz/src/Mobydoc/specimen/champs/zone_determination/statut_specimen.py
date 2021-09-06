import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneDeterminationStatutSpecimen(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDeterminationStatutSpecimen"

    id = Column("ChampSpecimenZoneDeterminationStatutSpecimen_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_determination = Column("ChampSpecimenZoneDeterminationStatutSpecimen_SpecimenZoneDetermination_Id", UUID, ForeignKey("SpecimenZoneDetermination.SpecimenZoneDetermination_Id"), nullable=True)

    from ....reference.statut_specimen import StatutSpecimen as t_statut_specimen
    id_statut_specimen = Column("ChampSpecimenZoneDeterminationStatutSpecimen_StatutSpecimen_Id", UUID, ForeignKey(t_statut_specimen.id), nullable=True)

    ordre = Column("ChampSpecimenZoneDeterminationStatutSpecimen_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    statut_specimen = relationship(t_statut_specimen, foreign_keys=[id_statut_specimen])
    
    #qualificatif_date...
    zone_determination = relationship("SpecimenZoneDetermination", foreign_keys=[id_zone_determination])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['ordre'] = self.ordre
        data['statut_specimen'] = json_test(self.statut_specimen)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data        