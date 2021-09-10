from pyramid.settings import asbool, aslist
import sys
#import types
PY2 = sys.version_info[0] == 2

import os,datetime,logging
l = logging.getLogger('ppssauth')

if PY2:
    def is_nonstr_iter(v):
        return hasattr(v, '__iter__')
else:
    def is_nonstr_iter(v):
        if isinstance(v, str):
            return False
        return hasattr(v, '__iter__')

def getBT(version = 4):
    v4 = version == 4
    return {
        'xs': 'col-' if v4 else 'col-xs-'
    }

class Conf():

    @classmethod
    def tplpath(cls, filename, layout=False):
        path = ""
        if cls.templatepackage:
            path += cls.templatepackage + ":"
        if layout:
            path += cls.templatelayoutfolder
        else:
            path += cls.templatefolder
        return path + "/" + filename + "." + cls.templateextension

    @staticmethod
    def conf2list(confval,default=None):
        try:
            if not is_nonstr_iter(confval):
                #print(repr(confval))
                confval = aslist(confval,flatten=False)
            print(repr(confval))
            return confval
        except Exception as e:
            l.exception(u"Exception parsing value:{}".format(confval))
            if default is None:
                raise e
            else:
                return default

    @staticmethod
    def parseSmtp(val):
        """ 
            try to parse smtp uri in a (user,password,host,port) tuple
            Full format:
            user:password@host:port
            optionals:
            [user[:password]@]host[:port]
        """
        if val is None:
            return None,None,None,None
        try:
            
            user = None
            password = None
            host = None
            port = 25
            at = s.rfind('@')
            if at>0:
                hostpart = val[at:]
                userpart = val[:at]
            else:
                hostpart = val
                userpart = None
            if userpart:
                colonindex = userpart.find(":")
                if colonindex>=0:
                    user = userpart[:colonindex]
                    password = userpart[colonindex:]
                else:
                    user = userpart
            colonindex = hostpart.find(":")
            if colonindex>=0:
                host,post = hostpart.split(":")
            else:
                host = hostpart
            return user,password,host,port
        except Exception as e:
            l.exception("error parsing smtp value '{}'".formaT(val))
            return None,None,None,None


    @classmethod
    def setup(cls, settings):
        cls.adminname   =settings.get("ppss_auth.adminname", "admin")
        cls.adminpass   =settings.get("ppss_auth.adminpass", "")
        cls.initdb = settings.get("ppss_auth.initdb", "true").lower() == 'true'

        # routes
        cls.loginurl = settings.get("ppss_auth.login_url", "/login")
        cls.logouturl = settings.get("ppss_auth.logout_url", "/logout")
        cls.postlogoutroute = settings.get("ppss_auth.post_logout_route", "ppsslogin")
        cls.postloginroute = settings.get("ppss_auth.post_login_route", "home")
        cls.postloginfollow = settings.get("ppss_auth.post_login_follow", "true").lower() == 'true'

        cls.backfromppssauth = settings.get("ppss_auth.back_from_ppss_auth",None)
        
        # NEW USER REGISTRATION
        cls.registeruurl = settings.get("ppss_auth.register_url", "/register")
        cls.usercanregister = settings.get("ppss_auth.canregister", "false").lower() == "true"
        cls.activationemail = settings.get("ppss_auth.register_requireactivation", "true").lower() != "false"
        cls.activationemailtpl = settings.get("ppss_auth.register_activationemailtpl","")

        cls.saltforhash = settings.get("ppss_auth.salt", "ImTheSaltOfThisLife")

        cls.forbiddentologin = settings.get("ppss_auth.forbidden_to_login", "true").lower() == 'true'


        #password enforcement
        cls.passwordpreviousdifferent = int(settings.get("ppss_auth.password_previuos_diff","3"))
        cls.passwordrelist = Conf.conf2list( settings.get("ppss_auth.password_relist",["[A-Z]+","[a-z]+","[0-9]+","[!,\.\?\\/;:_\-+*@\£\$\%\&\(\)\"\'=\^àèìòùé\#§°ç{}]+"]) )
        cls.passwordwrongmessage = 'La nuova password deve essere differente dalle precedenti 3 e avere almeno una maiuscola, una minuscola, un numero e un carattere fra "!,.?\\/;:_-+*".'
        cls.passwordexpiredmessage = 'Password expired. Please change it.'
        cls.passwordexpire =  int(settings.get("ppss_auth.password_expire",0)  )


        ##template path
        cls.templatepackage =       settings.get("ppss_auth.templatepackage", "ppss_auth")
        cls.templatefolder =        settings.get("ppss_auth.templatefolder", "/templates")
        cls.templatelayoutfolder =  settings.get("ppss_auth.templatelayoutfolder", "/templates/layouts")
        cls.templateextension =     settings.get("ppss_auth.templateextension", "mako")

        #public templates
        cls.logintemplate = settings.get("ppss_auth.logintemplate", cls.tplpath("login") )
        cls.changepasswordtemplate = settings.get("ppss_auth.changepasswordtemplate", cls.tplpath("change") )
        cls.publictemplateinherit = settings.get("ppss_auth.publictemplateinherit", cls.tplpath("public", True) )
        
        #bo template
        cls.listusertemplate = settings.get("ppss_auth.listuser_template", cls.tplpath("listuser") )
        cls.editusertemplate = settings.get("ppss_auth.edituser_template", cls.tplpath("edituser") )
        cls.listgrouptemplate = settings.get("ppss_auth.listgroup_template", cls.tplpath("listgroup") )
        cls.editgrouptemplate = settings.get("ppss_auth.editgroup_template", cls.tplpath("editgroup") )
        cls.listpermtemplate = settings.get("ppss_auth.listperm_template", cls.tplpath("listperm") )
        cls.editpermtemplate = settings.get("ppss_auth.editperm_template", cls.tplpath("editperm") )
        cls.registerusertemplate = settings.get("ppss_auth.registeruser_template", cls.tplpath("registeruser") )

        cls.botemplateinherit = settings.get("ppss_auth.botemplateinherit", cls.tplpath("public", True) )
        

        #bo template inheritance
        cls.mastertemplateinherit = settings.get("ppss_auth.mastertemplateinherit", cls.tplpath("masterlayout", True) )
        cls.sectiontemplateinherit = settings.get("ppss_auth.sectiontemplateinherit", cls.tplpath("midlayout", True) )

        cls.bootstrapClasses = getBT(int(settings.get("ppss_auth.bootstrapversion",4)))

        cls.testurl = settings.get("ppss_auth.testurl", "/test")

        #functionalities
        cls.newusergroups = [x for x in map(str.strip, ( settings.get("ppss_auth.newusergroups", '' ).split(",") ) ) if x  ]


        #Setup user, groups and permissions
        cls.perm2create = Conf.conf2list( settings.get("ppss_auth.permission_list",[])  )
        cls.group2create = Conf.conf2list( settings.get("ppss_auth.group_list",[])  )
        cls.user2create = Conf.conf2list( settings.get("ppss_auth.user_list",[])  )
        cls.defaultpassword = settings.get("ppss_auth.default_password",None)  
        


        #session names
        cls.sessionuser = 'ppss_auth_loggeduser'
        cls.sessionprincipals = 'ppss_auth_principals'
        cls.sessionpermissions = 'ppss_auth_permissions'


        cls.idclient = "896890850990-kdppue1lijfhkj5s7tu8lsh7gsj99ndj.apps.googleusercontent.com"
        cls.secret = "hhuJLuYo9ZnvAVd9XopH-s8n"


        #SMTP
        cls.smtpuri = settings.get("ppss_auth.smpt",None)
        cls.smtpuser,cls.smtppassword,cls.smtphost,cls.smtport = Conf.parseSmtp(cls.smtpuri)
        cls.mailsender = settings.get("ppss_auth.mailsender",None)
