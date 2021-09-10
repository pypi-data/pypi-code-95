from pyramid.i18n import TranslationStringFactory
_ = TranslationStringFactory('ppss_auth')


#def __(request,mystring ):
#  return request.localizer.translate( _(mystring),domain="ppss_auth" )

def __(request,mystr,*args,domain='ppss_auth',**kwargs):
  ts = _(mystr)
  if len(args) == 1:
    return request.localizer.pluralize(ts,'',args[0],domain=domain,**kwargs)  
  return request.localizer.translate(ts,domain=domain,**kwargs)