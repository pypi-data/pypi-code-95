import uuid

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text, Boolean)
from sqlalchemy.orm import relationship

from ..base import UUID, Base, indent, json_test


class Reference(Base):
    # table definitions
    __tablename__ = "Reference"

    id = Column("Reference_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    code = Column("Reference_CodeReference", INTEGER, nullable=False)
    id_zone_generale = Column("Reference_ZoneGenerale_Id", UUID, ForeignKey("ReferenceZoneGenerale.ReferenceZoneGenerale_Id"), nullable=False)
    type_name = Column("_typeName", String(256), nullable=False)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons
    zone_generale = relationship("ReferenceZoneGenerale", foreign_keys=[id_zone_generale])

    @property
    def label(self):
        return self.zone_generale.libelle if self.zone_generale else None

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['code'] = self.code
        data['zone_generale'] = json_test(self.zone_generale)
        data['type_name'] = self.type_name

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user
        data['t_version'] = self.t_version.hex()

        return data    

class ReferenceZoneGenerale(Base):
    # table definitions
    __tablename__ = "ReferenceZoneGenerale"

    id = Column("ReferenceZoneGenerale_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    libelle = Column("ReferenceZoneGenerale_Libelle", String(200), nullable=True)
    note_application = Column("ReferenceZoneGenerale_NoteApplication", String, nullable=True)
    is_protege = Column("ReferenceZoneGenerale_IsProtege", Boolean, nullable=True)
    id_reference_fichier = Column("ReferenceZoneGenerale_ReferenceFichier_Id", UUID, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['libelle'] = self.libelle
        data['note_application'] = self.note_application
        data['is_protege'] = self.is_protege

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data    

