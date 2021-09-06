import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, Float, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_loop, json_tags, json_test


class ProvenanceZoneBibliographie(Base):
    # définition de table
    __tablename__ = "ProvenanceZoneBibliographie"

    id = Column("ProvenanceZoneBibliographie_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_provenance = Column("ProvenanceZoneBibliographie_Provenance_Id", UUID, ForeignKey("Provenance.Provenance_Id"), nullable=True)
    from ..reference.type_information import TypeInformation as t_type_information
    id_type_information = Column("ProvenanceZoneBibliographie_TypeInformation_Id", UUID, ForeignKey(t_type_information.id), nullable=True)
    from ..notice_bibliographique.notice_bibliographique import NoticeBibliographique as t_notice_bibliographique
    id_reference_bibliographique = Column("ProvenanceZoneBibliographie_ReferenceBibliographique_Id", UUID, ForeignKey(t_notice_bibliographique.id), nullable=True)
    notes = Column("ProvenanceZoneBibliographie_Notes", String, nullable=True)
    ordre = Column("ProvenanceZoneBibliographie_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    #
    #
    #

    provenance_obj =  relationship("Provenance", foreign_keys=[id_provenance])
    type_information_obj = relationship(t_type_information, foreign_keys=[id_type_information])
    reference_bibliographique_obj = relationship(t_notice_bibliographique, foreign_keys=[id_reference_bibliographique])

    #
    #
    #

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['type_information'] = json_test(self.type_information_obj)
        data['reference_bibliographique'] = json_test(self.reference_bibliographique_obj)
        data['notes'] = self.notes

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
