import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test
from .reference import Reference

class TypeInformation(Base):
    # table definitions
    __tablename__ = "TypeInformation"

    id = Column("Reference_Id", UUID, ForeignKey("Reference.Reference_Id"), primary_key=True, nullable=False, default=uuid.uuid4)
    id_zone_contexte = Column("TypeInformation_ZoneContexte_Id", UUID, ForeignKey("TypeInformationZoneContexte.TypeInformationZoneContexte_Id"), nullable=True)

    # liaisons
    reference = relationship(Reference, foreign_keys=[id])
    zone_contexte = relationship("TypeInformationZoneContexte", foreign_keys=[id_zone_contexte], post_update=True)
    
    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['reference'] = json_test(self.reference)
        data['zone_contexte'] = json_test(self.zone_contexte)

        return data

class TypeInformationZoneContexte(Base):
    __tablename__ = "TypeInformationZoneContexte"

    id = Column("TypeInformationZoneContexte_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    
    id_type_information_fichier = Column("TypeInformationZoneContexte_TypeInformationFichier_Id", UUID, nullable=True)
    id_parent = Column("TypeInformationZoneContexte_Parent_Id", UUID, nullable=True)
    id_voir = Column("TypeInformationZoneContexte_Voir_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['id_type_information_fichier'] = self.id_type_information_fichier
        data['id_parent'] = self.id_parent
        data['id_voir'] = self.id_voir

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data    
