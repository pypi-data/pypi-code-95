import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneDatationGeologiqueDatationGeologique(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDatationGeologiqueDatationGeologique"

    id = Column("ChampSpecimenZoneDatationGeologiqueDatationGeologique_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_datation_geologique = Column("ChampSpecimenZoneDatationGeologiqueDatationGeologique_SpecimenZoneDatationGeologique_Id", \
        UUID, ForeignKey("SpecimenZoneDatationGeologique.SpecimenZoneDatationGeologique_Id"), nullable=True)
    from ....datation_geologique.datation_geologique import DatationGeologique as t_datation_geologique
    id_datation_geologique = Column("ChampSpecimenZoneDatationGeologiqueDatationGeologique_DatationGeologique_Id", UUID, \
        ForeignKey(t_datation_geologique.id), nullable=True)
    from ....reference.qualificatif_date import QualificatifDate as t_qualificatif_date
    id_qualificatif_date = Column("ChampSpecimenZoneDatationGeologiqueDatationGeologique_QualificatifDatation_Id", UUID, \
        ForeignKey(t_qualificatif_date.id), nullable=True)
    ordre = Column("ChampSpecimenZoneDatationGeologiqueDatationGeologique_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    # Links
    # 

    zone_datation_geologique = relationship("SpecimenZoneDatationGeologique", foreign_keys=[id_zone_datation_geologique])
    #datation_geologique = relationship(t_datation_geologique, foreign_keys=[id_datation_geologique])
    datation_geologique = relationship(t_datation_geologique, foreign_keys=[id_datation_geologique])
    qualificatif_datation = relationship(t_qualificatif_date, foreign_keys=[id_qualificatif_date])

    #
    # external links
    #

    # 
    # generate json representation
    # 

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['datation_geologique'] = json_test(self.datation_geologique)
        data['qualificatif_datation'] = json_test(self.qualificatif_datation)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data