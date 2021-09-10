import logging
l = logging.getLogger('ppssauth')

def configRoutes(config,Conf):
  from .views.auth import AuthController

  config.include("pyramid_beaker")
  config.add_static_view(  name='ppss_auth_static', path='ppss_auth_static', cache_max_age=3600)
  config.add_route('ppsslogin', Conf.loginurl)
  config.add_route('ppsslogout', Conf.logouturl)


  config.add_route('ppss:user:register', Conf.registeruurl)

  config.add_route('ppss:user:changepassword', '/password/change')
  config.add_route('ppss:user:resetpassword', '/password/change/{magicnumber}')
  
  config.add_route('ppss:user:list', '/user/list')
  config.add_route('ppss:user:editself', '/user/modify/me')
  config.add_route('ppss:user:edit', '/user/modify/{elementid}')
  config.add_route('ppss:user:search', '/user/search/')

  config.add_route('ppss:group:list', '/group/list')
  config.add_route('ppss:group:edit', '/group/modify/{elementid}')
  
  config.add_route('ppss:group:removeuser', '/group/removeuser/{elementid}/{targetid}')
  config.add_route('ppss:group:adduser', '/group/adduser/{elementid}/{targetid}')
  config.add_route('ppss:group:removeperm', '/group/removeperm/{elementid}/{targetid}')
  config.add_route('ppss:group:addperm', '/group/addperm/{elementid}/{targetid}')
  config.add_route('ppss:group:search', '/group/search/')

  config.add_route('ppss:perm:list',   '/perm/list')
  config.add_route('ppss:perm:edit',   '/perm/modify/{elementid}')
  config.add_route('ppss:perm:delete', '/perm/delete/{elementid}')
  config.add_route('ppss:perm:search', '/perm/search/')

  config.add_route('ppss:user:remove', '/user/remove/{userid}/{groupid}')
  config.add_route('ppss:user:checkpassword', '/user/checkpassword/{userid}')

  config.add_route('test:test',Conf.testurl)


  config.add_route('oauth:callback',"/oauth/callback")

  ########views

  #config.add_view(AuthController,attr='login',route_name="ppsslogin", renderer=Conf.logintemplate)
  #config.add_view(AuthController,attr='logout',route_name="ppsslogout")
  #config.add_view(AuthController,attr='ppsschangepassword',route_name="ppss:user:changepassword", 
  #    renderer=Conf.changepasswordtemplate)

  if Conf.forbiddentologin:
      config.add_forbidden_view(AuthController,attr='login',renderer=Conf.logintemplate)
  
  config.add_view(AuthController,attr='listUser',route_name="ppss:user:list",
      permission="listuser", renderer=Conf.listusertemplate)
  config.add_view(AuthController,attr='editUser',route_name="ppss:user:edit",
      permission="edituser", renderer=Conf.editusertemplate)
  config.add_view(AuthController,attr='editUser',route_name="ppss:user:editself",
      permission="login", renderer=Conf.editusertemplate)
  


  config.add_view(AuthController,attr='listGroup',route_name="ppss:group:list",
      permission="listuser", renderer=Conf.listgrouptemplate)
  config.add_view(AuthController,attr='editGroup',route_name="ppss:group:edit",
      permission="edituser", renderer=Conf.listgrouptemplate)

  config.add_view(AuthController,attr='listPerm',route_name="ppss:perm:list",
      permission="sysadmin", renderer=Conf.listpermtemplate)
  config.add_view(AuthController,attr='editPerm',route_name="ppss:perm:edit",
      permission="sysadmin", renderer=Conf.listpermtemplate)
  config.add_view(AuthController,attr='deletePerm',route_name="ppss:perm:delete",
      permission="sysadmin", renderer=Conf.listpermtemplate)

  config.add_view(AuthController,attr='checkPassword',route_name="ppss:user:checkpassword",
      permission="login", renderer=Conf.editpermtemplate)


  config.add_view(AuthController,attr='addPerm2Group',route_name='ppss:group:addperm',
    permission="sysadmin",renderer="json")
  config.add_view(AuthController,attr='removePerm2Group',route_name='ppss:group:removeperm',
    permission="sysadmin",renderer="json")
  config.add_view(AuthController,attr='addUser2Group',route_name='ppss:group:adduser',
    permission="sysadmin",renderer="json")
  config.add_view(AuthController,attr='removUser2Group',route_name='ppss:group:removeuser',
    permission="sysadmin",renderer="json")


  config.add_view(AuthController,attr='registernewuser',route_name='ppss:user:register',
    renderer=Conf.registerusertemplate)


  config.add_view(AuthController,attr='oauthCallBack',route_name='oauth:callback')



