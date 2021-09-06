import uuid

from sqlalchemy import TIMESTAMP, Table, Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship, backref

from ..base import UUID, Base, indent, json_test, json_tags

class MobyTag_Personne_PersonneZoneIdentification_MobyTag(Base):
    __tablename__ = "MobyTag_Personne_PersonneZoneIdentification_MobyTag"

    id_tag = Column("MobyTag_Id", UUID, ForeignKey("MobyTag.MobyTag_Id"), primary_key=True, nullable=False)
    id_personne = Column("PersonneZoneIdentification_Id", UUID, ForeignKey("PersonneZoneIdentification.PersonneZoneIdentification_Id"), primary_key=True, nullable=False)

    from ..moby.tag.mobytag import MobyTag
    tag = relationship(MobyTag)

class PersonneZoneIdentification(Base):
    __tablename__ = "PersonneZoneIdentification"

    id = Column("PersonneZoneIdentification_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_type_personne = Column("PersonneZoneIdentification_TypePersonne_Id", UUID, nullable=True)
    id_civilite_prefixe = Column("PersonneZoneIdentification_CivilitePrefixe_Id", UUID, nullable=True)
    nom = Column("PersonneZoneIdentification_Nom", String(256), nullable=False)
    prenom = Column("PersonneZoneIdentification_Prenom", String(256), nullable=True)
    complement_nom = Column("PersonneZoneIdentification_ComplementNom", String, nullable=True)
    sexe = Column("PersonneZoneIdentification_Sexe", String(1), nullable=True)
    
    # wtf are those 3 things doing here ??
    numero_adherent = Column("PersonneZoneIdentification_NumeroAdherent", String, nullable=True)
    validite_cotisation = Column("PersonneZoneIdentification_ValiditeCotisation", String, nullable=True)
    id_autorisation_pret = Column("PersonneZoneIdentification_AutorisationPret_Id", UUID, nullable=True)

    # Personne.Personne_Id
    id_personne_fichier = Column("PersonneZoneIdentification_PersonneFichier_Id", UUID, ForeignKey("Personne.Personne_Id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons
    #import mobydoc.personne.personne as m_personne
    l_personne = relationship("Personne", foreign_keys=[id_personne_fichier])

    tags = relationship("MobyTag_Personne_PersonneZoneIdentification_MobyTag")

    @property
    def nom_entier(self):
        nom = []
        if self.prenom:
            nom.append(self.prenom)
        if self.nom: 
            nom.append(self.nom)
        return ' '.join(nom)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['id_type_personne'] = self.id_type_personne
        data['id_civilite_prefixe'] = self.id_civilite_prefixe
        data['nom'] = self.nom
        data['prenom'] = self.prenom
        data['complement_nom'] = self.complement_nom
        data['sexe'] = self.sexe
        data['numero_adherent'] = self.numero_adherent
        data['validite_cotisation'] = self.validite_cotisation
        data['id_autorisation_pret'] = self.id_autorisation_pret
        data['id_personne_fichier'] = self.id_personne_fichier
        data['backlink_to_personne'] = (self.l_personne.id_zone_identification == self.id)

        data['tags'] = json_tags(self.tags)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data        
        