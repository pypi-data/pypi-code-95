import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneDeterminationDateDermination(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDeterminationDateDetermination"

    id = Column("ChampSpecimenZoneDeterminationDateDetermination_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_date_determination = Column("ChampSpecimenZoneDeterminationDateDetermination_DateDetermination_Id", UUID, ForeignKey("Datation.Datation_Id"), nullable=True)
    id_qualificatif_date = Column("ChampSpecimenZoneDeterminationDateDetermination_QualificatifDate_Id", UUID, ForeignKey("QualificatifDate.Reference_Id"), nullable=True)
    id_zone_determination = Column("ChampSpecimenZoneDeterminationDateDetermination_SpecimenZoneDetermination_Id", UUID, ForeignKey("SpecimenZoneDetermination.SpecimenZoneDetermination_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    from ....datation.datation import Datation as t_datation
    date = relationship(t_datation, foreign_keys=[id_date_determination])
    
    #qualificatif_date...
    zone_determination = relationship("SpecimenZoneDetermination", foreign_keys=[id_zone_determination])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['date'] = json_test(self.date)

        # does not seem to be used by the compactus. we'll see that later
        data['id_qualificatif_date'] = self.id_qualificatif_date

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data        