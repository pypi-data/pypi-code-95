import uuid

from sqlalchemy import TIMESTAMP, Column, DateTime, ForeignKey, String, text, Integer
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import relationship

from ...base import UUID, Base, indent

class MobyTag(Base):
    __tablename__ = "MobyTag"

    id = Column("MobyTag_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    id_picasso = Column("MobyTag_PicassoNom", Integer, nullable=False)
    tag = Column("MobyTag_Tag", String(255), nullable=False)
    id_parent = Column("MobyTag_Parent_Id", UUID, ForeignKey("MobyTag.id"), nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)

    # liaisons


    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['id_picasso'] = self.id_picasso
        data['tag'] = self.tag
        data['id_parent'] = self.id_parent

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data
    
