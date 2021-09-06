import uuid

from sqlalchemy import (INTEGER, TIMESTAMP, Column, DateTime, ForeignKey,
                        String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test


class ClassificationZoneContexte(Base):
    __tablename__ = "ClassificationZoneContexte"

    id = Column("ClassificationZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_classification_fichier = Column("ClassificationZoneContexte_ClassificationFichier_Id", UUID, ForeignKey("Classification.Classification_Id"), nullable=True)
    id_parent = Column("ClassificationZoneContexte_Parent_Id", UUID, ForeignKey("Classification.Classification_Id"), nullable=True)
    id_voir = Column("ClassificationZoneContexte_Voir_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # links
    classification = relationship("Classification", foreign_keys=[id_classification_fichier])
    parent = relationship("Classification", foreign_keys=[id_parent])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['parent'] = json_test(self.parent)
        data['id_voir'] = self.id_voir

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
