import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneCollecteProvenance(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneCollecteProvenance"

    id = Column("ChampSpecimenZoneCollecteProvenance_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_collecte = Column("ChampSpecimenZoneCollecteProvenance_SpecimenZoneCollecte_Id", UUID, ForeignKey("SpecimenZoneCollecte.SpecimenZoneCollecte_Id"), nullable=True)
    from ....provenance.provenance import Provenance as t_provenance
    id_provenance = Column("ChampSpecimenZoneCollecteProvenance_Provenance_Id", UUID, ForeignKey(t_provenance.id), nullable=True)
    ordre = Column("ChampSpecimenZoneCollecteProvenance_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    zone_collecte = relationship("SpecimenZoneCollecte", foreign_keys=[id_zone_collecte], back_populates='provenances')
    provenance = relationship(t_provenance, foreign_keys=[id_provenance])

    #
    # external links
    #

    # 
    # generate json representation
    # 

    @property
    def tree(self):
        return self.provenance.tree

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['provenance'] = json_test(self.provenance)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data