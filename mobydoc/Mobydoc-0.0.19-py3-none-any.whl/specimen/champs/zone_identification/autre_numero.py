import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenAutreNumero(Base):
    # définition de table
    __tablename__ = "ChampSpecimenAutreNumero"

    id = Column("ChampSpecimenAutreNumero_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_identification = Column("ChampSpecimenAutreNumero_SpecimenZoneIdentification_Id", UUID, ForeignKey("SpecimenZoneIdentification.SpecimenZoneIdentification_Id"), nullable=True)
    id_autre_numero = Column("ChampSpecimenAutreNumero_AutreNumero_Id", UUID, ForeignKey("AutreNumero.Reference_Id"), nullable=True)
    valeur = Column("ChampSpecimenAutreNumero_Valeur", String(256), nullable=True)
    ordre = Column("ChampSpecimenAutreNumero_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    zone_identification = relationship("SpecimenZoneIdentification", foreign_keys=[id_zone_identification])
    from ....reference.autre_numero import AutreNumero as t_autre_numero
    autre_numero = relationship(t_autre_numero, foreign_keys=[id_autre_numero])

    @property
    def label(self):
        return self.autre_numero.label if self.autre_numero else None

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['autre_numero'] = json_test(self.autre_numero)
            
        data['valeur'] = self.valeur
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data      
