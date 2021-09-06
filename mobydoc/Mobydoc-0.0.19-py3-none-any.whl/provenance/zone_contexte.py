import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, Float, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags, json_test


class ProvenanceZoneContexte(Base):
    # définition de table
    __tablename__ = "ProvenanceZoneContexte"

    id = Column("ProvenanceZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_provenance = Column("ProvenanceZoneContexte_ProvenanceFichier_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)
    id_parent = Column("ProvenanceZoneContexte_Parent_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)
    id_voir = Column("ProvenanceZoneContexte_Voir_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    provenance_obj =  relationship("Provenance", foreign_keys=[id_provenance])
    parent_obj =  relationship("Provenance", foreign_keys=[id_parent])
    voir_obj =  relationship("Provenance", foreign_keys=[id_voir])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['parent'] = json_test(self.parent_obj)
        data['voir'] = json_test(self.voir_obj)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
