import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, Float, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags, json_test


class DatationGeologiqueZoneContexte(Base):
    # définition de table
    __tablename__ = "DatationGeologiqueZoneContexte"

    id = Column("DatationGeologiqueZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_datation_geologique = Column("DatationGeologiqueZoneContexte_DatationGeologiqueFichier_Id", UUID, \
        ForeignKey("DatationGeologique.DatationGeologique_Id"), nullable=True)
    id_parent = Column("DatationGeologiqueZoneContexte_Parent_Id", UUID, ForeignKey("DatationGeologique.DatationGeologique_Id"), nullable=True)
    id_voir = Column("DatationGeologiqueZoneContexte_Voir_Id", UUID, ForeignKey("DatationGeologique.DatationGeologique_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    datation_geologique_obj =  relationship("DatationGeologique", foreign_keys=[id_datation_geologique])
    parent_obj =  relationship("DatationGeologique", foreign_keys=[id_parent])
    voir_obj =  relationship("DatationGeologique", foreign_keys=[id_voir])

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
