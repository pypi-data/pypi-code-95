import json, uuid, sys

from sqlalchemy import TIMESTAMP, Column, DateTime, String, text
from sqlalchemy.dialects.mssql import BIT
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER as UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#CURRENT_VERSION='7.1.348.2'
#CURRENT_VERSION='7.1.358.5'
#CURRENT_VERSION='7.1.384.2'
#CURRENT_VERSION='7.1.429.2'
CURRENT_VERSION='7.1.457.4'

class Version(Base):
    # définitions de table
    __tablename__ = "Version"

    id = Column("Version_Id", UUID, primary_key=True, nullable=False, default=uuid.uuid4)

    current = Column("Version_Current", String(256), nullable=True)
    updated_date = Column("Version_UpdatedDate", DateTime, nullable=True)
    is_modele_initialise = Column("Version_IsModeleInitialise", BIT, nullable=True)

    t_write = Column("_trackLastWriteTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_creation = Column("_trackCreationTime", DateTime, nullable=False, server_default=text("(getdate())"))
    t_write_user = Column("_trackLastWriteUser", String(64), nullable=False)
    t_creation_user = Column("_trackCreationUser", String(64), nullable=False)
    t_version = Column("_rowVersion", TIMESTAMP, nullable=False)


def indent(string):
    lines = string.split("\n")
    s = ''
    for l in lines:
        if l:
            s+= "  %s\n"%(l)
    return s

def _json(record):
    if isinstance(record, dict):
        data = {}
        for k in record:
            data[k] = _json(record[k])
        return data
    elif isinstance(record, list):
        data = []
        for v in record:
            data.append(_json(v))
        return data
    else:
        if isinstance(record, Base):
            try:
                data = record.json
            except AttributeError as e:
                return "object %s not supported\n%s\n%s\n%s"%(record.__class__.__name__, str(type(e)), str(e.args), str(e))
            else:
                return data
        return record

def dumps(record):
    record = _json(record)
    print(json.dumps(record, indent=4))
    return record

def json_test(o):
    if o:
        return o.json
    return None

def json_loop(object_list):
    l = []
    for o in object_list:
        l.append(o.json)
    return l

def json_tags(tags):
    l = []
    for t in tags:
        l.append(t.tag.json)
    return l

def checkVersion(dbsession):
    if not dbsession:
        print("invalid database session '%s'"%(repr(dbsession)), file=sys.stderr)
        return False
    print("checking database version %s"%(str(dbsession)), file=sys.stderr)
    version = dbsession.query(Version).order_by(Version.updated_date.desc()).first()
    if not version:
        print("Unable to find a version in the database", file=sys.stderr)
        return False
    print("Mobydoc database version %s setup on %s"%(version.current, version.updated_date.isoformat()), file=sys.stderr)
    if version.current != CURRENT_VERSION:
        print("Mobydoc database expected version %s"%(CURRENT_VERSION))
    return True
    # disable as it's a pain in the rear end everytime the stupid windows app upgrades.
    # lets hope we don't break anything
    ## return version.current == CURRENT_VERSION
