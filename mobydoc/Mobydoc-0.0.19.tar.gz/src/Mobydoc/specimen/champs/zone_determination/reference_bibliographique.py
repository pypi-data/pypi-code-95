import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship

from ....base import UUID, Base, indent, json_test


class ChampSpecimenZoneDeterminationReferenceBibliographique(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneDeterminationReferenceBibliographique"

    id = Column("ChampSpecimenZoneDeterminationReferenceBibliographique_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)


    id_zone_determination = Column("ChampSpecimenZoneDeterminationReferenceBibliographique_SpecimenZoneDetermination_Id", UUID, ForeignKey("SpecimenZoneDetermination.SpecimenZoneDetermination_Id"), nullable=True)

    id_reference_bibliographique = Column("ChampSpecimenZoneDeterminationReferenceBibliographique_ReferenceBibliographique_Id", UUID, ForeignKey("NoticeBibliographique.NoticeBibliographique_Id"), nullable=True)
    ordre = Column("ChampSpecimenZoneDeterminationReferenceBibliographique_Ordre", INTEGER, nullable=True)
    
    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    from ....notice_bibliographique.notice_bibliographique import NoticeBibliographique as t_notice_bibliographique
    reference_bibliographique = relationship(t_notice_bibliographique, foreign_keys=[id_reference_bibliographique])
    
    #qualificatif_date...
    zone_determination = relationship("SpecimenZoneDetermination", foreign_keys=[id_zone_determination])

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id
        data['ordre'] = self.ordre

        data['reference_bibliographique'] = json_test(self.reference_bibliographique)

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data        