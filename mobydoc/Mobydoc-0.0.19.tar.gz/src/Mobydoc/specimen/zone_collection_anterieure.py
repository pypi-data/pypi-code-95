import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_test
from ..reference.type_information import TypeInformation


class SpecimenZoneCollectionAnterieure(Base):
    # définition de table
    __tablename__ = "SpecimenZoneCollectionAnterieure"

    id = Column("SpecimenZoneCollectionAnterieure_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_specimen = Column("SpecimenZoneCollectionAnterieure_Specimen_Id", UUID, ForeignKey("Specimen.Specimen_Id"), nullable=True)

    from ..personne.personne import Personne as t_personne
    id_type_collection_anterieure = Column("SpecimenZoneCollectionAnterieure_TypeCollectionAnterieure_Id", UUID, nullable=True)
    id_collection_anterieure = Column("SpecimenZoneCollectionAnterieure_CollectionAnterieure_Id", UUID, ForeignKey(t_personne.id), nullable=True)
    id_vente_publique = Column("SpecimenZoneCollectionAnterieure_VentePublique_Id", UUID, nullable=True)
    id_lieu = Column("SpecimenZoneCollectionAnterieure_Lieu_Id", UUID, nullable=True)

    notes = Column("SpecimenZoneCollectionAnterieure_Notes", String, nullable=True)
    ordre = Column("SpecimenZoneCollectionAnterieure_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # 
    # relationships
    #

    specimen = relationship("Specimen", foreign_keys=[id_specimen])
    collection_anterieure = relationship(t_personne, foreign_keys=[id_collection_anterieure])

    #
    # object properties
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['id_type_collection_anterieure'] = self.id_type_collection_anterieure
        data['collection_anterieure'] = json_test(self.collection_anterieure)
        data['id vente_publique'] = self.id_vente_publique
        data['id_lieu'] = self.id_lieu

        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data

