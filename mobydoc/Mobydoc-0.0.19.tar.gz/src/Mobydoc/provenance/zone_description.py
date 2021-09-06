import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, Float, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags, json_test


class ProvenanceZoneDescription(Base):
    # définition de table
    __tablename__ = "ProvenanceZoneDescription"

    id = Column("ProvenanceZoneDescription_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    description = Column("ProvenanceZoneDescription_Description", String, nullable=True)
    id_provenance = Column("ProvenanceZoneDescription_ProvenanceFichier_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    provenance_obj =  relationship("Provenance", foreign_keys=[id_provenance])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['description'] = self.description

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
