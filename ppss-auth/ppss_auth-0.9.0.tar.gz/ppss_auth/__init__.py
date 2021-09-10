

#from views.auth import ppssauthpolicy,ACLRoot,getPrincipals
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
import transaction
import zope.sqlalchemy

from pyramid.i18n import get_localizer

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from .constants import Conf
from .models import initdb,PPSsuser
from .routes import configRoutes
from .ppss_auth_utils.db import checkDBRevision

import logging
l = logging.getLogger('ppssauth')


from pyramid.security import (
    Everyone, Authenticated,
    remember,forget,
    Allow,
    Everyone,ALL_PERMISSIONS
    )


def initAuthDb(settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    factory = sessionmaker()
    factory.configure(bind=engine)
    #dbsession = get_tm_session(session_factory, transaction.manager)
    dbsession = factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction.manager)
    try:
        checkDBRevision(engine = engine,
            session = dbsession)
    except Exception as e:
        l.exception("you need to upgrade the database.\nTo upgrade, run:\nppss_auth_upgrade_db <your pyramid ini file>.ini")
        raise e
    with transaction.manager:
        initdb(dbsession,Conf.initdb)

def getLoggedUser(request,addinsession=False):
    uid = request.session[Conf.sessionuser]['id'] if Conf.sessionuser in request.session else False
    user = request.session[Conf.sessionuser]['user'] if Conf.sessionuser in request.session else False
    if user:
        if addinsession:
            request.dbsession.add(user)
        return user
    else:
        return None
    #l.warn("*****getting logged user for {}".format(uid))
    if uid:
        user = PPSsuser.byId(uid,request.dbsession)
        return user
    else:
        pass
        #l.warn("**** session is:{}.\nI was looking for this key:{} -> {}".format(request.session,Conf.sessionuser,request.session.get(Conf.sessionuser,None)))
    return None
    

def add_renderer_globals(event):
    # ...
    request = event['request']
    event['_'] = request.translate
    event['_p'] = request.pluralize
    event['localizer'] = request.localizer

#tsf = TranslationStringFactory('YOUR_GETTEXT_DOMAIN')
from .ppss_auth_utils import _ as tsf

def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)
    defaultdomain = tsf('ppss_auth').domain
    def auto_translate(*args, **kwargs):
        return localizer.translate(tsf(*args, **kwargs))
    def auto_pluralize(src,num, *args,**kwargs):
        thisdomain = kwargs['domain'] if 'domain' in kwargs else defaultdomain
        return localizer.pluralize(tsf(src,*args, **kwargs),'',num,domain=thisdomain)
    request.localizer = localizer
    request.translate = auto_translate
    request.pluralize = auto_pluralize

def getPPSSAuthConf(request):
    return Conf


configured = False
def includeme(config):
    global configured
    if configured:
        l.debug("already configured...")
        #return
    configured = True
    #ppssauthpolicy = PPSSAuthenticationPolicy(config.get_settings())
    settings = config.get_settings()
    Conf.setup(settings)
    config.add_request_method(getLoggedUser,'loggeduser',reify=True)
    
    config.add_translation_dirs('ppss_auth:locale/')

    config.add_subscriber(add_renderer_globals,
                          'pyramid.events.BeforeRender')
    config.add_subscriber(add_localizer,
                          'pyramid.events.NewRequest')

    config.add_request_method(getPPSSAuthConf,'ppssauthconf',reify=True)
    initAuthDb(settings)

    configRoutes(config,Conf)
    
    from .views.auth import getPrincipals,ACLRoot
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(SessionAuthenticationPolicy(callback=getPrincipals) )
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_root_factory(ACLRoot)
    config.scan("ppss_auth")
    pass
