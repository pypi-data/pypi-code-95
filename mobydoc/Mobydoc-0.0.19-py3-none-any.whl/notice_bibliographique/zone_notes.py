import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent

class NoticeBibliographiqueZoneNotes(Base):
    # définition de table
    __tablename__ = "NoticeBibliographiqueZoneNotes"

    id = Column("NoticeBibliographiqueZoneNotes_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_notice_bibliographique = Column("NoticeBibliographiqueZoneNotes_NoticeBibliographique_Id", UUID, ForeignKey("NoticeBibliographique.NoticeBibliographique_Id"), nullable=True)
    notes = Column("NoticeBibliographiqueZoneNotes_Notes", String, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    #
    #
    #

    notice_bibliographique_obj = relationship("NoticeBibliographique", foreign_keys=[id_notice_bibliographique])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data
