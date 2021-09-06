import uuid

from sqlalchemy import (BIGINT, Boolean, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_tags


class CaracteristiquesPhysiquesZoneGenerale_MobyTag_MobyTag_CaracteristiquesPhysiques(Base):
    __tablename__ = "CaracteristiquesPhysiquesZoneGenerale_MobyTag_MobyTag_CaracteristiquesPhysiques"

    id_tag = Column("MobyTag_Id", UUID, ForeignKey("MobyTag.MobyTag_Id"), primary_key=True, nullable=False)
    id_caracteristiques_physiques = Column("CaracteristiquesPhysiquesZoneGenerale_Id", UUID, \
        ForeignKey("CaracteristiquesPhysiquesZoneGenerale.CaracteristiquesPhysiquesZoneGenerale_Id"), primary_key=True, nullable=False)

    from ..moby.tag.mobytag import MobyTag
    tag = relationship(MobyTag)


class CaracteristiquesPhysiquesZoneGenerale(Base):
    __tablename__ = "CaracteristiquesPhysiquesZoneGenerale"

    id = Column("CaracteristiquesPhysiquesZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_caracteristiques_physiques = Column("CaracteristiquesPhysiquesZoneGenerale_CaracteristiquesPhysiquesFichier_Id", UUID, \
        ForeignKey("CaracteristiquesPhysiques.CaracteristiquesPhysiques_Id"), nullable=True)

    caracteristiques_physiques = Column("CaracteristiquesPhysiquesZoneGenerale_CaracteristiquesPhysiques", String(200), nullable=True)
    notes = Column("CaracteristiquesPhysiquesZoneGenerale_Notes", String, nullable=True)
    is_protege = Column("CaracteristiquesPhysiquesZoneGenerale_IsProtege", Boolean, nullable=True)
    
    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # internal links
    #

    caracteristiques_physiques_obj = relationship("CaracteristiquesPhysiques", foreign_keys=[id_caracteristiques_physiques])

    # 
    # external links
    # 

    tags = relationship(CaracteristiquesPhysiquesZoneGenerale_MobyTag_MobyTag_CaracteristiquesPhysiques)

    #
    # dumps json
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['caracteristiques_physiques'] = self.caracteristiques_physiques
        data['notes'] = self.notes
        data['is_protege'] = self.is_protege

        data['tags'] = json_tags(self.tags)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        
        return data
