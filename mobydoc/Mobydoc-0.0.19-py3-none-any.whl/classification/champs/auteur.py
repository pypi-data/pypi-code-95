import uuid

from sqlalchemy import (INTEGER, TIMESTAMP, Column, DateTime, ForeignKey,
                        String, text)
from sqlalchemy.orm import relationship

from ...base import UUID, Base, indent

class ChampClassificationZoneIdentificationAuteur(Base):
    __tablename__ = "ChampClassificationZoneIdentificationAuteur"

    id = Column("ChampClassificationZoneIdentificationAuteur_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_zone_identification = Column("ChampClassificationZoneIdentificationAuteur_ClassificationZoneIdentification_Id", UUID, 
        ForeignKey("ClassificationZoneIdentification.ClassificationZoneIdentification_Id"), nullable=True)
    # Personne.Personne_Id
    id_auteur = Column("ChampClassificationZoneIdentificationAuteur_Auteur_Id", UUID, ForeignKey("Personne.Personne_Id"), nullable=True)
    appliquer_parenthesage = Column("ChampClassificationZoneIdentificationAuteur_AppliquerParenthesage", INTEGER, nullable=True)
    ordre = Column("ChampClassificationZoneIdentificationAuteur_Ordre", INTEGER, nullable=True, default=1)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    zone_identification = relationship("ClassificationZoneIdentification", foreign_keys=[id_zone_identification], post_update=True, back_populates="auteurs")

    from ...personne.personne import Personne as t_personne
    personne = relationship(t_personne, foreign_keys=[id_auteur], post_update=True)

    def __str__(self):
        return self.nom_auteur

    @property
    def nom_auteur(self):
        return self.personne.nom_entier

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        if self.personne:
            data['personne'] = self.personne.json
        data['appliquer_parenthesage'] = self.appliquer_parenthesage
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
