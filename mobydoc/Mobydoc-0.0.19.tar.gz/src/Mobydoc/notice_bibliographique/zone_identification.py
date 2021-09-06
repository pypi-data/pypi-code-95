import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_tags


class MobyTag_NoticeBibliographique_NoticeBibliographiqueZoneIdentification_MobyTag(Base):
    __tablename__ = "MobyTag_NoticeBibliographique_NoticeBibliographiqueZoneIdentification_MobyTag"

    id_tag = Column("MobyTag_Id", UUID, ForeignKey("MobyTag.MobyTag_Id"), primary_key=True, nullable=False)
    id_personne = Column("NoticeBibliographiqueZoneIdentification_Id", UUID, ForeignKey("NoticeBibliographiqueZoneIdentification.NoticeBibliographiqueZoneIdentification_Id"), primary_key=True, nullable=False)

    from ..moby.tag.mobytag import MobyTag
    tag = relationship(MobyTag)


class NoticeBibliographiqueZoneIdentification(Base):
    __tablename__ = "NoticeBibliographiqueZoneIdentification"

    id = Column("NoticeBibliographiqueZoneIdentification_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    id_notice_bibliographique = Column("NoticeBibliographiqueZoneidentification_NoticeBibliographique_Id", UUID, ForeignKey("NoticeBibliographique.NoticeBibliographique_Id"), nullable=True)

    # seems there is only "1" as a value
    type_notice = Column("NoticeBibliographiqueZoneIdentification_TypeNotice", INTEGER, nullable=True, default=1)
    identification = Column("NoticeBibliographiqueZoneIdentification_Identification", String(200), nullable=True)
    moby_cle = Column("NoticeBibliographiqueZoneIdentification_MobyCle", String(256), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    # internal links
    #

    notice_bibliographique = relationship("NoticeBibliographique", foreign_keys=[id_notice_bibliographique])

    # 
    # external links
    # 

    tags = relationship("MobyTag_NoticeBibliographique_NoticeBibliographiqueZoneIdentification_MobyTag")

    #
    # dumps json
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['type_notice'] = self.type_notice
        data['identification'] = self.identification
        data['moby_cle'] = self.moby_cle
        
        data['tags'] = json_tags(self.tags)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
