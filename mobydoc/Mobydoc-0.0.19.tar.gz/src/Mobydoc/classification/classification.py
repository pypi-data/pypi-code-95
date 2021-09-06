import uuid

from sqlalchemy import (TIMESTAMP, Column, DateTime, ForeignKey, String,
                        column, func, select, text)
from sqlalchemy.orm import column_property, relationship

from ..base import UUID, Base, indent, json_test


class Classification(Base):
    __tablename__ = "Classification"

    id = Column("Classification_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    # ClassificationZoneIdentification.ClassificationZoneIdentification_Id
    id_zone_identification = Column("Classification_ZoneIdentification_Id", UUID, ForeignKey("ClassificationZoneIdentification.ClassificationZoneIdentification_Id"), nullable=False)
    id_zone_donnees_geographiques = Column("Classification_ZoneDonneesGeographiques_Id", UUID, nullable=True)
    id_zone_datation_geologique = Column("Classification_ZoneDatationGeologique_Id", UUID, nullable=True)
    id_zone_protection = Column("Classification_ZoneProtection_Id", UUID, nullable=True)
    id_zone_mot_cle = Column("Classification_ZoneMotCle_Id", UUID, nullable=True)
    # ClassificationZoneContexte.ClassificationZoneContexte_Id
    id_zone_contexte = Column("Classification_ZoneContexte_Id", UUID, ForeignKey("ClassificationZoneContexte.ClassificationZoneContexte_Id"), nullable=True)
    id_zone_informations_systeme = Column("Classification_ZoneInformationsSysteme_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons
    from .zone_identification import ClassificationZoneIdentification as t_zone_identification
    zone_identification = relationship(t_zone_identification, foreign_keys=[id_zone_identification])
    from .zone_contexte import ClassificationZoneContexte as t_zone_contexte
    zone_contexte = relationship(t_zone_contexte, foreign_keys=[id_zone_contexte])

    # for now, gives the zone_contextes to which this classification is a parent
    children_zone_contexte = relationship(t_zone_contexte, primaryjoin=id==t_zone_contexte.id_parent)
    nb_children = column_property(select([func.count(t_zone_contexte.id)]).where(t_zone_contexte.id_parent==id).correlate_except(t_zone_contexte))

    # children_b = relationship("Classification", secondary=t_zone_contexte,
    #                         primaryjoin="id==ClassificationZoneContexte.id_parent",
    #                         secondaryjoin="ClassificationZoneContexte.id_classification_fichier==id")

    # @property
    # def nb_children(self):
    #     if self.children_zone_contexte:
    #         return len(self.children_zone_contexte)
    #     return 0

    @property
    def children(self):
        c = []
        for c_zc in self.children_zone_contexte:
            c.append(c_zc.classification)
        return c


    @property
    def parent(self):
        if self.zone_contexte:
            if self.zone_contexte.parent:
                return parent
        return None

    @property
    def parent_name(self):
        if self.zone_contexte and self.zone_contexte.parent:
            return str(self.zone_contexte.parent)
        return ''

    @property
    def tree(self):
        tree_data = []
        if self.zone_contexte and self.zone_contexte.parent:
            tree_data = self.zone_contexte.parent.tree
        tree_data.append(self)
        return tree_data

    @property
    def name_tree(self):
        names = []
        if self.zone_contexte and self.zone_contexte.parent:
            names = self.zone_contexte.parent.name_tree
        if self.zone_identification.nom:
            names.append(self.zone_identification.nom)
        else:
            names.append("(unknown)")
        return names

    @property
    def name_tree_detailed(self):
        names = []
        if self.zone_contexte and self.zone_contexte.parent:
            names = self.zone_contexte.parent.name_tree_detailed
        data = {}
        data['name'] = self.zone_identification.nom
        data['date'] = self.zone_identification.date
        if data['date']:
            data['date'] = str(data['date'])
        authors = []
        for a in self.zone_identification.auteurs:
            author = {}
            author['last_name'] = a.personne.zone_identification.nom
            author['first_name'] = a.personne.zone_identification.prenom
            authors.append(author)
        data['authors'] = authors
        names.append(data)
        return names


    def __str__(self):
        if self.zone_identification.nom:
            return self.zone_identification.nom  
        return '(unknown)'

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_identification'] = json_test(self.zone_identification)
        data['id_zone_donnes_geographiques'] = self.id_zone_donnees_geographiques
        data['id_zone_datation_geologique'] = self.id_zone_datation_geologique
        data['id_zone_protection'] = self.id_zone_protection
        data['id_zone_mot_cle'] = self.id_zone_mot_cle
        data['zone_contexte'] = json_test(self.zone_contexte)
        data['id_zone_informations_systeme'] = self.id_zone_informations_systeme

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
