import uuid
import logging

from sqlalchemy import (BIGINT, DATETIME, INTEGER, TIMESTAMP, VARBINARY,
                        Column, DateTime, ForeignKey, String, text)
from sqlalchemy.orm import relationship, object_session

from ...base import UUID, Base, indent, json_test

log = logging.getLogger(__name__)

class ChampSpecimenZoneMultimediaMultimedia(Base):
    # définition de table
    __tablename__ = "ChampSpecimenZoneMultimediaMultimedia"

    id = Column("ChampSpecimenZoneMultimediaMultimedia_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    from ..zone_multimedia import SpecimenZoneMultimedia
    id_zone_multimedia = Column("ChampSpecimenZoneMultimediaMultimedia_SpecimenZoneMultimedia_Id", UUID, ForeignKey(SpecimenZoneMultimedia.id), nullable=True)
    from ...multimedia.multimedia import Multimedia as t_multimedia
    id_multimedia = Column("ChampSpecimenZoneMultimediaMultimedia_Multimedia_Id", UUID, ForeignKey(t_multimedia.id), nullable=True)
    ordre = Column("ChampSpecimenZoneMultimediaMultimedia_Ordre", INTEGER, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)

    # liaisons

    multimedia = relationship(t_multimedia, foreign_keys=[id_multimedia])
    zone_multimedia = relationship(SpecimenZoneMultimedia, foreign_keys=[id_zone_multimedia], back_populates='multimedias')

    def __init__(self, zone_multimedia, ordre=1, *args, **kwargs):
        self.zone_multimedia = zone_multimedia
        self.ordre = ordre
        self.t_write_user = text("(USER)")
        self.t_creation_user = text("(USER)")
        super().__init__(*args, **kwargs)

    @property
    def json(self):
        data = {}
        data['_type'] = self.__class__.__name__
        data['id'] = self.id

        data['multimedia'] = json_test(self.multimedia)
        data['ordre'] = self.ordre

        data['t_write'] = self.t_write.isoformat()
        data['t_creation'] = self.t_creation.isoformat()
        data['t_write_user'] = self.t_write_user
        data['t_creation_user'] = self.t_creation_user

        return data

    @property
    def path(self):
        if self.multimedia:
            return self.multimedia.path
        return "(NOT SET)"

    def updatePath(self, win_path):
        if self.multimedia:
            log.info("UPDATING %d TO '%s'"%(self.ordre, win_path))
            return self.multimedia.updatePath(win_path)
        
        # there is no multimedia. need to create it...
        from ...multimedia.multimedia import Multimedia
        from ...multimedia.zone_generale import MultimediaZoneGenerale
        
        session = object_session(self)
        
        mzg = MultimediaZoneGenerale()
        session.add(mzg)

        mm = Multimedia()
        log.info('mm id: %s'%(mm.id))
        mm.zone_generale = mzg
        session.add(mm)

        self.multimedia = mm

        log.info('multimedia.id %s %s'%(self.id_multimedia, mm.id))

        log.info("new Multimedia added to session")

        mm.updatePath(win_path)

        log.info("path updated")

        return True