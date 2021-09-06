import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampNoticeBibliographiqueTitrePropre(Base):
    __tablename__ = "ChampNoticeBibliographiqueTitrePropre"

    id = Column("ChampNoticeBibliographiqueTitrePropre_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_zone_titre = Column("ChampNoticeBibliographiqueTitrePropre_NoticeBibliographique_Id", UUID, ForeignKey("NoticeBibliographiqueZoneTitre.NoticeBibliographiqueZoneTitre_Id"), nullable=True)

    from ....titre.titre import Titre as t_titre
    id_titre_propre = Column("ChampNoticeBibliographiqueTitrePropre_TitrePropre_Id", UUID, ForeignKey(t_titre.id), nullable=True)
    ordre = Column("ChampNoticeBibliographiqueTitrePropre_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    zone_titre = relationship("NoticeBibliographiqueZoneTitre", foreign_keys=[id_zone_titre])
    titre_propre = relationship(t_titre, foreign_keys=[id_titre_propre])

    #
    # json
    # 


    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['titre_propre'] = json_test(self.titre_propre)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
