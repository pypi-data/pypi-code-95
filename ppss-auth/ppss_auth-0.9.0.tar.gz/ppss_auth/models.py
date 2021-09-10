import sys
PY2 = sys.version_info[0] == 2
if not PY2:
    unicode = str

from sqlalchemy import (
    Table,
    Column,
    Index,
    Integer,
    Text,
    Unicode,UnicodeText,
    DateTime,
    ForeignKey,
    desc, asc,UniqueConstraint
)
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData
NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

from datetime import datetime,timedelta

import logging,uuid

from sqlalchemy.orm import joinedload

metadata = MetaData(naming_convention=NAMING_CONVENTION)
Base = declarative_base(metadata=metadata)

from .constants import Conf
from .ppss_auth_utils.password import getPasswordDigest


l = logging.getLogger('ppssauth.models')


class constants():
    SYSADMINPERM = "sysadmin"
    SYSADMINGROUP = "sysadmin"

def __createPermissions(session,permissions):
    permmap = {}
    for p in permissions:
        perm = session.query(PPSspermission).filter(PPSspermission.name == p['name']).first()
        if not perm:
            perm = PPSspermission(name = p['name'])
            session.add(perm)
            l.info("permission '{}' added to session".format(p['name']))
        perm.permtype = p['permtype'] if 'permtype' in p else 0
        permmap[p['name'] ] = perm
    return permmap

def __createGroups(session,groups,permissions):
    groupmap = {}
    for g in groups:
        g = g.split("=")
        gname = str.strip(g[0])
        if len(g) == 2:
            permlist = map(str.strip,g[1].split(","))
        else:
            permlist = []
        group = session.query(PPSsgroup).filter(PPSsgroup.name == gname).first()
        if not group:
            group = PPSsgroup(name = gname)
            session.add(group)
            l.info("group '{}' added to session".format(gname))
        groupmap[gname] = group
        for p in permlist:
            if not group.hasPermission(p):
                if p in permissions:
                    perm = permissions[p]
                else:
                    perm = PPSspermission(name = p,permtype = 0)
                    session.add(perm)
                    permissions[p] = perm
                    l.info("new permission '{}' created for group '{}'".format(p,gname))
                group.permissions.append(perm)
    return groupmap

def __createUsers(session,users,groups,defaultpassword = None):
    usermap = {}
    for u in users:
        u = u.split("=")
        uname = u[0].split("/")
        upassword = None
        if len(uname)==2:
            upassword = uname[1].strip()
        else: 
            upassword = Conf.defaultpassword
        uname = uname[0].strip()
        if len(u)==2:
            grouplist = map(str.strip,u[1].split(","))
        else:
            grouplist = []
        user = session.query(PPSsuser).filter(PPSsuser.username == uname).first()
        if not user:
            user = PPSsuser(username = uname)
            if upassword:
                user.setPassword(upassword)
            elif defaultpassword:
                user.setPassword(defaultpassword)
            session.add(user)
            l.info("user '{}' added to session".format(uname))
        usermap[uname] = user
        for g in grouplist:
            if not user.isInGroup(g,False):
                if g in groups:
                    group = groups[g]
                else:
                    group = session.query(PPSsgroup).filter(PPSsgroup.name == g).first()
                    if group is None:
                        group = PPSsgroup(name = g)
                        session.add(group)
                    else:
                        groups[g] = group
                    l.info("new group '{}' created for user '{}'".format(g,uname))
                user.groups.append(group)
    return usermap


##the caller must commit this
def initdb(session=None,createdefault=False,engine = None):
    if engine is None:
        engine = session.get_bind()
    try:
        PPSsuser.all(session)
    except:
        raise Exception("no user table. exiting!")
    if createdefault:
        l.info("creating default")
        systemperms = [#PPSspermission(name = u"admin"),
                {"name": u"edituser","permtype": 1},
                {"name": u"listuser","permtype": 1},
                {"name": u"login"   ,"permtype": 1},
                {"name": constants.SYSADMINPERM,"permtype": 1},
        ]
        permissions = [{'name':p,'permtype':1} for p in Conf.perm2create]
        for sp in systemperms:
            permissions.append(sp)

        permissionmap = __createPermissions(session,permissions)
        l.debug("permission map:{}".format(permissionmap))
        groupmap = __createGroups(session, Conf.group2create + ["useradmin=edituser,listuser,login","{}={}".format(constants.SYSADMINGROUP,constants.SYSADMINPERM)] , permissionmap)
        l.debug("group map:{}".format(groupmap))
        if Conf.adminname:
            root = __createUsers(session,[Conf.adminname+"="+constants.SYSADMINGROUP],groupmap,Conf.adminpass if Conf.adminpass else None)
        usermap = __createUsers(session, Conf.user2create, groupmap )
        l.debug("user map:{}".format(usermap))
        return 0
    
    return 0

ppssuserlkppssgroup = Table('ppssuser_lk_ppssgroup', Base.metadata,
    Column('user_id',Integer,ForeignKey('ppss_user.id', ondelete="CASCADE"), primary_key=True),
    Column('group_id',Integer,ForeignKey('ppss_group.id', ondelete="CASCADE"), primary_key=True )
)
ppssgrouplkppsspermission = Table('ppssgroup_lk_ppsspermission', Base.metadata,
    Column('group_id',Integer,ForeignKey('ppss_group.id', ondelete="CASCADE"), primary_key=True),
    Column('permission_id',Integer,ForeignKey('ppss_permission.id', ondelete="CASCADE"), primary_key=True )
)


class commonTable():
    @classmethod
    def byId(cls,id,dbsession):
        return dbsession.query(cls).filter(cls.id == id).first()

    @classmethod
    def all(cls,dbsession):
        return dbsession.query(cls).all()
    @classmethod
    def all(cls,DBSession,orderby=None,orderdir='asc'):
        q = DBSession.query(cls)
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()
        #return cls.orderAll(DBSession.query(cls)).all()

    @classmethod
    def byField(cls,field,value,DBSession,orderby=None,orderdir='asc'):
        q = DBSession.query(cls).filter(getattr(cls, field)==value)
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()
    
    @classmethod
    def byFields(cls,fields,DBSession,orderby=None,orderdir='asc'):
        q = DBSession.query(cls)
        for i,field in enumerate(fields):
            q = q.filter(getattr(cls, field[0])==field[1])
        if orderby is not None:
            if orderdir == 'asc':
                q = q.order_by(getattr(cls,orderby).asc() )
            else:
                q = q.order_by((getattr(cls,orderby).desc()  ))
        return q.all()


class PPSsuser(Base,commonTable):
    __tablename__   = 'ppss_user'
    id              = Column(Integer, primary_key=True)
    username        = Column(Unicode(128),unique=True)
    password        = Column(Unicode(1024))
    insertdt        = Column(DateTime,default=datetime.now)
    updatedt        = Column(DateTime,default=datetime.now,onupdate=datetime.now)
    lastlogin       = Column(DateTime)
    enabled         = Column(Integer,default=1) # 0 disabled, 1 active, -1 need activation
    magicnumber     = Column(Text(),default=uuid.uuid5(uuid.uuid4(),"bidibibodibibu" ).hex )   #Conf.saltforhash
    createdby       = Column(Integer)
    disabledby      = Column(Integer)
    passwordexpire  = Column(DateTime, default = None)

    groups = relationship("PPSsgroup",secondary=ppssuserlkppssgroup,lazy='joined',cascade="all", 
        backref=backref('users',lazy='select',order_by='PPSsuser.username'))


    superusercache = None
    permissionscache = None
    permissionsmapcache = None
    groupmapcache = None

    @classmethod
    def checkLogin(cls,user,password,dbsession):
        return PPSsuser.checkCryptedLogin(user,getPasswordDigest(password),dbsession)

    @classmethod
    def checkCryptedLogin(cls,user,password,dbsession):
        res = dbsession.query(cls).filter(cls.username==user).filter(cls.password==password).filter(cls.enabled==1) \
            .options(joinedload('groups')) \
            .options(joinedload('groups.permissions')) \
            .all()
        return res[0] if len(res)==1 else None

    def passwordExpired(self,now = None):
        if now is None:
            now = datetime.now()
        l.debug("user:{},now:{},expire:{},res:{}".format(self.username,now,self.passwordexpire,self.passwordexpire is None or self.passwordexpire>now))
        return not (self.passwordexpire is None or self.passwordexpire>now)

    def getPrincipals(self,expired=False):
        if expired:
            return ['ppss_auth:changepassword']
        else:
            return [str("g:"+group.name ) for group in self.groups  ] 

    def todict(self):
        return { "id": self.id, "username":self.username,"enabled":self.enabled}


    def setPassword(self,password,canexpire = True):
        dig = getPasswordDigest(password)
        self.password= dig
        if Conf.passwordexpire and canexpire:
            self.passwordexpire = datetime.now() + timedelta(days = Conf.passwordexpire)
        self.passowrdhistory.append( PPSspasswordhistory(password = dig)  )
        return self


    def getPermissions(self):
        if self.permissionscache is None:
            result = set()
            for g in self.groups:
                if g.enabled:
                    for p in g.permissions:
                        result.add( (p.id, p.name, p.permtype) )
            self.permissionscache = list(set(result))
        return self.permissionscache
        # return set([p.name for p in [g.permissions for g in self.groups if g.enabled]] )

    def getPermissionsMap(self):
        if self.permissionsmapcache is None:
            permlist = self.getPermissions()
            self.permissionsmapcache = set([p[1] for p in permlist])
        return self.permissionsmapcache

    def isSuperUser(self):
        if self.superusercache is None:
            self.superusercache = False
            l.info("checking if {} is superuser against this name:'{}' and permissions:{}".format(self.username,Conf.adminname,self.getPermissionsMap()  ))
            if self.username == Conf.adminname:
                self.superusercache = True
            elif 'sysadmin' in self.getPermissionsMap():
                self.superusercache = True
            else:
                l.info("not a super user: {}".format( self.getPermissionsMap() ))
        return self.superusercache

    def hasPermission(self, permission):
        if self.isSuperUser():
            return True
        return permission in self.getPermissionsMap()

    def getGroupsMap(self):
        if self.groupmapcache is None:
            grouplist = []
            for g in self.groups:
                grouplist.append(g.name)
            self.groupmapcache = set(grouplist)
        return self.groupmapcache


    def isInGroup(self,groupname,whitelie=True):
        if self.isSuperUser() and whitelie:return True
        return groupname in self.getGroupsMap()

    def __unicode__(self):
        return u"<PPSsuser ({id}-{name},{enabled})>".format(id=self.id,name=self.username, enabled=self.enabled)

    def __str__(self): 
        return self.__unicode__()

class PPSspasswordhistory(Base):
    __tablename__   = 'ppss_passwordhistory'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('ppss_user.id'))
    insertdt        = Column(DateTime,default=datetime.now)
    password        = Column(Unicode(1024))

    user = relationship("PPSsuser", backref=backref('passowrdhistory',order_by="desc(PPSspasswordhistory.id)" ))

class PPSsloginhistory(Base):
    __tablename__   = 'ppss_loginhistory'
    id              = Column(Integer, primary_key=True)
    user_id         = Column(Integer, ForeignKey('ppss_user.id'))
    ipaddress       = Column(Unicode(128))
    insertdt        = Column(DateTime,default=datetime.now)


class PPSsgroup(Base,commonTable):
    __tablename__   = 'ppss_group'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128),unique=True)
    enabled= Column(Integer,default=1)
    permissions = relationship("PPSspermission",cascade="all",secondary=ppssgrouplkppsspermission  ,backref=backref('groups'))

    permissionsmapcache = None
    permissionscache = None

    def __unicode__(self):
        return u"<PPSsgroup {name} ({id})>".format(name=self.name,id=self.id)
    def __str__(self):
        return self.__unicode__()

    def todict(self):
        return {'id':self.id,"name":self.name}

    def userdict(self):
        return [x.todict() for x in self.users]

    def permdict(self):
        return [x.todict() for x in self.permissions]

    def getPermissionsMap(self):
        if self.permissionsmapcache is None:
            self.permissionscache = []
            for p in self.permissions:
                self.permissionscache.append(p.name)
            self.permissionsmapcache = set(self.permissionscache)
        return self.permissionsmapcache

    def hasPermission(self,permissionname):
        return permissionname in self.getPermissionsMap()

    @classmethod
    def byName(cls,name,dbsession):
        return dbsession.query(cls).filter(cls.name==name).first()

class PPSspermission(Base,commonTable):
    __tablename__   = 'ppss_permission'
    id     = Column(Integer, primary_key=True)
    name   = Column(Unicode(128),unique=True)
    permtype   = Column(Integer,default=0)  #1 is for built-in permissions
    systemperm = Column(Unicode(4),default=u'y')

    def __unicode__(self):
        return u"<PPSspermission {name} ({id})>".format(name=self.name,id=self.id)
    def __str__(self):
        return self.__unicode__()

    def todict(self):
        return {'id':self.id,"name":self.name,"permtype":self.permtype}


import pkg_resources  # part of setuptools

class DBVersion(Base):
    __tablename__   = 'module_db_version'
    modulename = Column(Unicode(128),primary_key=True)
    moduleversion = Column(Unicode(64),primary_key=True)
    dbversion = Column(Unicode(64))
    insertdt  = Column(DateTime,default=datetime.now,onupdate=datetime.now)

    myname = "ppss_auth"

    @staticmethod
    def updateDB(session):
        version = session.query(DBVersion).filter(DBVersion.modulename == DBVersion.myname).first()
        moduldeversion = pkg_resources.require("ppss_auth")[0].version
        l.debug("read version in db {} module version {}".format(version,moduldeversion) )
        if version is None:
            session.add(DBVersion(modulename=DBVersion.myname,moduleversion=moduldeversion,dbversion="1.0") ) 
        else:
            version.moduleversion = moduldeversion
            version.dbversion = "1.0"