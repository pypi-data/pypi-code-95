import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent

class SpecimenZoneInformationsSysteme(Base):
    # définition de table
    __tablename__ = "SpecimenZoneInformationsSysteme"

    id = Column("SpecimenZoneInformationsSysteme_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_specimen = Column("SpecimenZoneInformationsSysteme_SpecimenFichier_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)
    creation_time = Column("SpecimenZoneInformationsSysteme_CreationTime", DateTime, nullable=False)
    creation_user = Column("SpecimenZoneInformationsSysteme_CreationUser", String(256), nullable=False)
    last_write_time = Column("SpecimenZoneInformationsSysteme__trackLastWriteTime", DateTime, nullable=False)
    last_write_user = Column("SpecimenZoneInformationsSysteme_LastWriteUser", String(256), nullable=False)
    id_institution = Column("SpecimenZoneInformationsSysteme_Institution_Id", UUID, nullable=True)
    statut_notice = Column("SpecimenZoneInformationsSysteme_StatutNotice", INTEGER, nullable=True)
    diffusion_notice = Column("SpecimenZoneInformationsSysteme_DiffusionNotice", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    specimen_obj = relationship("Specimen", foreign_keys=[id_specimen])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['creation_time'] = self.creation_time.isoformat()
        data['creation_user'] = self.creation_user
        data['last_write_time'] = self.last_write_time.isoformat()
        data['last_write_user'] = self.last_write_user
        data['id_institution'] = self.id_institution
        data['statut_notice'] = self.statut_notice
        data['diffusion_notice'] = self.diffusion_notice

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
