import uuid

from sqlalchemy import (INTEGER, TIMESTAMP, Column, DateTime, ForeignKey,
                        String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_test


class ClassificationZoneIdentification(Base):
    TYPES_NOMENCLATURE = { 1: 'Autre', 2: 'Botanique', 3: 'Zoologie' }

    __tablename__ = "ClassificationZoneIdentification"

    id = Column("ClassificationZoneIdentification_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    # 1. Autre
    # 2. Botanique
    # 3. Zoologie
    id_type_nomenclature = Column("ClassificationZoneIdentification_TypeNomenclature", INTEGER, nullable=False)
    nom = Column("ClassificationZoneIdentification_Nom", String, nullable=True)
    # Datation.Datation_Id
    id_date = Column("ClassificationZoneIdentification_Date_Id", UUID, ForeignKey("Datation.Datation_Id"), nullable=True)
    # Fossile.Reference_Id
    id_fossile = Column("ClassificationZoneIdentification_Fossile_Id", UUID, nullable=True)
    id_rang_taxonomique = Column("ClassificationZoneIdentification_RangTaxonomique_Id", UUID, ForeignKey("RangTaxonomique.Reference_Id"), nullable=True)
    # Classification.Classification_Id
    id_classification_fichier = Column("ClassificationZoneIdentification_ClassificationFichier_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    from ..datation.datation import Datation as t_datation
    date = relationship(t_datation, foreign_keys=[id_date])
    from ..reference.rang_taxonomique import RangTaxonomique as t_rang_taxonomique
    rang_taxonomique = relationship(t_rang_taxonomique, foreign_keys=[id_rang_taxonomique])

    # ChampClassificationZoneIdentificationAuteur
    from .champs.auteur import ChampClassificationZoneIdentificationAuteur as t_auteur
    auteurs = relationship(t_auteur, back_populates="zone_identification", order_by="ChampClassificationZoneIdentificationAuteur.ordre")

    @property
    def type_nomenclature(self):
        if self.id_type_nomenclature in self.TYPES_NOMENCLATURE:
            return self.TYPES_NOMENCLATURE[self.id_type_nomenclature]
        else:
            return "UNKNOWN"

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        type_nomenclature = {}
        type_nomenclature['id'] = self.id_type_nomenclature
        type_nomenclature['name'] = self.type_nomenclature
        data['type_nomenclature'] = type_nomenclature

        data['nom'] = self.nom
        data['date'] = json_test(self.date)
        data['id_fossile'] = self.id_fossile
        data['rang_taxonomique'] = json_test(self.rang_taxonomique)
        data['auteurs'] = json_loop(self.auteurs)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
