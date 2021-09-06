import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test, json_loop


class NoticeBibliographique(Base):
    __tablename__ = "NoticeBibliographique"

    id = Column("NoticeBibliographique_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    from .zone_identification import NoticeBibliographiqueZoneIdentification as t_zone_identification
    id_zone_identification = Column("NoticeBibliographique_ZoneIdentification_Id", UUID, ForeignKey(t_zone_identification.id), nullable=False)
    id_zone_mention_edition = Column("NoticeBibliographique_ZoneMentionEdition_Id", UUID, nullable=True)
    id_zone_numerotation = Column("NoticeBibliographique_ZoneNumerotation_Id", UUID, nullable=True)
    id_zone_description_physique = Column("NoticeBibliographique_ZoneDescriptionPhysique_Id", UUID, nullable=True)
    id_zone_periodicite = Column("NoticeBibliographique_ZonePeriodicite_Id", UUID, nullable=True)
    from .zone_notes import NoticeBibliographiqueZoneNotes as t_zone_notes
    id_zone_notes = Column("NoticeBibliographique_ZoneNotes_Id", UUID, ForeignKey(t_zone_notes.id), nullable=True)
    id_zone_resume = Column("NoticeBibliographique_ZoneResume_Id", UUID, nullable=True)
    id_zone_cles_auteur = Column("NoticeBibliographique_ZoneClesAuteur_Id", UUID, nullable=True)
    id_zone_donnees_codees = Column("NoticeBibliographique_ZoneDonneesCodees_Id", UUID, nullable=True)
    id_zone_notice_liee = Column("NoticeBibliographique_ZoneNoticeLiee_Id", UUID, nullable=True)
    from .zone_informations_systeme import NoticeBibliographiqueZoneInformationsSysteme as t_zone_informations_systeme
    id_zone_informations_systeme = Column("NoticeBibliographique_ZoneInformationsSysteme_Id", UUID, ForeignKey(t_zone_informations_systeme.id), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    # internal links
    #

    zone_identification = relationship(t_zone_identification, foreign_keys=[id_zone_identification])
    zone_notes = relationship(t_zone_notes, foreign_keys=[id_zone_notes])
    zone_informations_systeme = relationship(t_zone_informations_systeme, foreign_keys=[id_zone_informations_systeme])

    #
    # external links
    #

    from .zone_adresse_publication import NoticeBibliographiqueZoneAdressePublication as t_zone_adresse_publication
    zones_adresse_publication = relationship(t_zone_adresse_publication, back_populates="notice_bibliographique", order_by=t_zone_adresse_publication.ordre)    

    # ZoneCatalogage
    # ZoneCollection
    # ZoneImpression
    # ZoneIndicesSystematiques
    # ZoneMotCle
    # ZoneMultimedia
    # ZoneNumeroStandard

    from .zone_titre import NoticeBibliographiqueZoneTitre as t_zone_titre
    zones_titre = relationship(t_zone_titre, back_populates="notice_bibliographique", order_by=t_zone_titre.ordre)    

    #
    # output to json
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['zone_identification'] = json_test(self.zone_identification)
        data['id_zone_mention_edition'] = self.id_zone_mention_edition
        data['id_zone_numerotation'] = self.id_zone_numerotation
        data['id_zone_description_physique'] = self.id_zone_description_physique
        data['id_zone_periodicite'] = self.id_zone_periodicite
        data['zone_notes'] = json_test(self.zone_notes)
        data['id_zone_resume'] = self.id_zone_resume
        data['id_zone_cles_auteur'] = self.id_zone_cles_auteur
        data['id_zone_donnees_codees'] = self.id_zone_donnees_codees
        data['id_zone_notice_liee'] = self.id_zone_notice_liee
        data['zone_informations_systeme'] = json_test(self.zone_informations_systeme)

        data['zones_adresse_publication'] = json_loop(self.zones_adresse_publication)
        data['zones_titre'] = json_loop(self.zones_titre)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
