import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent

class TitreZoneContexte(Base):
    # définition de table
    __tablename__ = "TitreZoneContexte"

    id = Column("TitreZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_titre = Column("TitreZoneContexte_TitreFichier_Id", UUID, ForeignKey("Titre.Titre_Id"), nullable=True)
    id_parent = Column("TitreZoneContexte_Parent_Id", UUID, ForeignKey("Titre.Titre_Id"), nullable=True)
    id_voir = Column("TitreZoneContexte_Voir_Id", UUID, ForeignKey("Titre.Titre_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    titre_obj = relationship("Titre", foreign_keys=[id_titre])
    parent_obj = relationship("Titre", foreign_keys=[id_parent])
    voir_obj = relationship("Titre", foreign_keys=[id_voir])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['parent'] = json_test(self.parent_obj)
        # this could be a cause of data loops. maybe we should be careful
        data['voir'] = json_test(self.voir_obj)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
