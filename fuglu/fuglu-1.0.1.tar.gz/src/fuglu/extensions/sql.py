# -*- coding: UTF-8 -*-
#   Copyright 2009-2021 Oli Schacher, Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Fuglu SQLAlchemy Extension
#
from io import StringIO
import logging
import traceback
import weakref
from fuglu.shared import default_template_values, FuConfigParser, Suspect, deprecated


modlogger = logging.getLogger('fuglu.extensions.sql')
STATUS = "not loaded"
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import scoped_session, sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    DeclarativeBase = declarative_base()
    
    SQL_EXTENSION_ENABLED = True
    STATUS = "available"
except ImportError:
    SQL_EXTENSION_ENABLED = False
    STATUS = "sqlalchemy not installed"
    DeclarativeBase = object

    def text(string):
        return string

ENABLED = SQL_EXTENSION_ENABLED # fuglu compatibility


_sessmaker = None
_engines = {}


def get_session(connectstring, **kwargs):
    global SQL_EXTENSION_ENABLED
    global _sessmaker
    global _engines

    if not SQL_EXTENSION_ENABLED:
        raise Exception("sql extension not enabled")

    if connectstring in _engines:
        engine = _engines[connectstring]
    else:
        engine = create_engine(connectstring, pool_recycle=20)
        _engines[connectstring] = engine

    if _sessmaker is None:
        _sessmaker = sessionmaker(autoflush=True, autocommit=True, **kwargs)

    session = scoped_session(_sessmaker)
    session.configure(bind=engine)
    return session


def lint_session(connectstring):
    if not connectstring:
        print('INFO: no SQL connection string found, not using SQL database')
        return True

    if not SQL_EXTENSION_ENABLED:
        print('WARNING: SQL extension not enabled, not using SQL database')
        return False

    try:
        dbsession = get_session(connectstring)
        dbsession.execute('SELECT 1')
    except Exception as e:
        print('ERROR: failed to connect to SQL database: %s' % str(e))
        return False
    return True


class DBFile(object):

    """A DB File allows storing configs in any rdbms. """

    def __init__(self, connectstring, query):
        self.connectstring = connectstring
        # eg. "select action,regex,description FROM tblname where scope=:scope
        self.query = query
        self.logger = logging.getLogger('fuglu.sql.dbfile')

    def getContent(self, templatevars=None):
        """Get the content from the database as a list of lines. If the query returns multiple columns, they are joined together with a space as separator
        templatevars: replace placeholders in the originalquery , eg. select bla from bla where domain=:domain
        """
        if templatevars is None:
            templatevars = {}
        sess = get_session(self.connectstring)
        res = sess.execute(self.query, templatevars)
        self.logger.debug('Executing query %s with vars %s' % (self.query, templatevars))
        buff = []
        for row in res:
            line = " ".join(filter(None, row))
            buff.append(line)
        sess.close()
        return buff


class DBConfig(FuConfigParser):

    """
    Runtime Database Config Overrides.
    Behaves like a RawConfigParser but returns global database overrides/domainoverrides/useroverrides if available
    """

    def __init__(self, config, suspect):
        super().__init__()
        self.logger = logging.getLogger('fuglu.sql.dbconfig')
        self.sectioncache = {}
        self.suspect = None
        self.set_suspect(suspect)
        self._clone_from(config)
    
    
    def set_suspect(self, suspect):
        if suspect is None:
            suspect = Suspect('', '', '/dev/null')
        # store weak reference to suspect
        # otherwise (python 3), the instance of DBConfig does not reduce the
        # refcount to suspect even if it goes out of scope and the suspect
        # object does not get freed until a (manual or automatic) run of the
        # garbage collector "gc.collect()"
        self.suspect = weakref.ref(suspect)
    
    
    def set_rcpt(self, recipient):
        suspect = Suspect('', recipient, '/dev/null')
        self.set_suspect(suspect)
    
    
    def _clone_from(self, config):
        """Clone this object from a RawConfigParser"""
        stringout = StringIO()
        config.write(stringout)
        stringin = StringIO(stringout.getvalue())
        del stringout
        self.read_file(stringin)
        del stringin
    
    
    def load_section(self, section):
        """
        load section into local cache.
        :param section: name of section to be loaded
        :return: True if loading was successful
        """
        if not SQL_EXTENSION_ENABLED or (not self.has_section('databaseconfig')) or (not self.has_option('databaseconfig', 'dbconnectstring')):
            return False
        connectstring = self.parentget('databaseconfig', 'dbconnectstring')
        if connectstring.strip() == '':
            return False
        query = self.parentget('databaseconfig', 'sqlsection')
        if query.strip() == '':
            return False
        
        session = get_session(connectstring)
        sqlvalues = {'section': section}
        default_template_values(self.suspect(), sqlvalues)
        try:
            result = session.execute(query, sqlvalues).fetchall()
            self.sectioncache[section] = result
        except Exception:
            trb = traceback.format_exc()
            self.logger.error("Error getting database config override section data: %s" % trb)
            return False
        return True
    
    
    def _get_cached(self, section, option):
        suspect = self.suspect()
        todomain = f'%{suspect.to_domain}'
        
        optionfield = self.parentget('databaseconfig', 'option_field')
        scopefield = self.parentget('databaseconfig', 'scope_field')
        valuefield = self.parentget('databaseconfig', 'value_field')
        
        try:
            for row in self.sectioncache.get(section, []):
                scope = getattr(row, scopefield)
                dboption = getattr(row, optionfield)
                if dboption == option and scope in {suspect.to_address, todomain}:
                    return getattr(row, valuefield)
        except AttributeError as e:
            self.logger.error('database layout does not match databaseconfig settings: %s' % str(e))
        return None
    
    
    def get(self, section, option, **kwargs):
        if not SQL_EXTENSION_ENABLED or (not self.has_section('databaseconfig')) or (not self.has_option('databaseconfig', 'dbconnectstring')):
            return self.parentget(section, option, **kwargs)
        
        connectstring = self.parentget('databaseconfig', 'dbconnectstring')
        if connectstring.strip() == '':
            #self.logger.debug('empty db connect string')
            return self.parentget(section, option, **kwargs)
        
        query = self.parentget('databaseconfig', 'sql')
        if query.strip() == '':
            return self.parentget(section, option, **kwargs)
        
        if section in self.sectioncache:
            return self._get_cached(section, option)
        
        session = get_session(connectstring)
        sqlvalues = {
            'section': section,
            'option': option,
        }
        default_template_values(self.suspect(), sqlvalues)
        
        result = None
        try:
            #self.logger.debug("Executing query '%s' with vars %s"%(query,sqlvalues))
            result = session.execute(query, sqlvalues).first()
        except Exception:
            trb = traceback.format_exc()
            self.logger.error("Error getting database config override: %s" % trb)
        
        session.remove()
        if result is None:
            #self.logger.debug('no result')
            return self.parentget(section, option, **kwargs)
        else:
            #self.logger.debug('result: '+result[0])
            return result[0]
    
    
    def parentget(self, section, option, **kwargs):
        return super().get(section, option, **kwargs)


# this function is ugly, use dbconfig instead...
@deprecated
def get_domain_setting(domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
    if logger is None:
        logger = logging.getLogger()

    cachekey = '%s-%s' % (cachename, domain)
    cached = cache.get_cache(cachekey)
    if cached is not None:
        logger.debug("got cached setting for %s" % domain)
        return cached

    settings = default_value

    try:
        session = get_session(dbconnection)

        # get domain settings
        dom = session.execute(sqlquery, {'domain': domain}).fetchall()

        if not dom or not dom[0] or len(dom[0]) == 0:
            logger.debug("Can not load domain setting - domain %s not found. Using default settings." % domain)
        else:
            settings = dom[0][0]

        session.remove()

    except Exception as e:
        logger.error("Exception while loading setting for %s : %s" % (domain, str(e)))

    cache.put_cache(cachekey, settings)
    logger.debug("refreshed setting for %s" % domain)
    return settings
