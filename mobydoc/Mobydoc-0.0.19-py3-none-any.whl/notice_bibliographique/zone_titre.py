import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop


class NoticeBibliographiqueZoneTitre(Base):
    __tablename__ = "NoticeBibliographiqueZoneTitre"

    id = Column("NoticeBibliographiqueZoneTitre_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_notice_bibliographique = Column("NoticeBibliographiqueZoneTitre_NoticeBibliographique_Id", UUID, ForeignKey("NoticeBibliographique.NoticeBibliographique_Id"), nullable=True)

    mention_responsabilite = Column("NoticeBibliographiqueZoneTitre_MentionResponsabilite", String, nullable=True)
    ordre = Column("NoticeBibliographiqueZoneTitre_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    #
    #

    notice_bibliographique = relationship("NoticeBibliographique", foreign_keys=[id_notice_bibliographique])

    #
    # 
    #

    from .champ.zone_titre.titre_propre import ChampNoticeBibliographiqueTitrePropre as t_titre_propre
    titres_propres = relationship(t_titre_propre, back_populates="zone_titre", order_by=t_titre_propre.ordre)    


    #
    # dumps json
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['titres_propres'] = json_loop(self.titres_propres)
        data['mention_responsabilite'] = self.mention_responsabilite

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
