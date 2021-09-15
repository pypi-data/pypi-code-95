"""
    Bottle CAS Server - APIs
"""
import sys
from urllib.parse import unquote, parse_qs, urlencode

from bottle import request, response, jinja2_template

from .cas_response import CASResponse
from .CasTicketManager import CasTicketManager
from .casSaml_request import cas_v3_samlValidate

class _Logger:
    """ Logger proxy to stderr """

    def info(self, *args, **kwargs):
        """ logger.info() """
        print('INFO', file=sys.stderr,  *args, **kwargs)


class CasBridge(CasTicketManager):

    def __init__(
            self,
            app,                # bottle() object
            auth,               # authentication provider (saml/oidc/etc)
            config = {},         # configs all have defaults
            backing = None,     # backing store for tickets
            logger = None,      # logger (default sys.stderr)
        ):
        """ Bottle API routes for the CAS service. """

        self.auth = auth
        self.app = app

        if logger is None: logger = _Logger()

        # Initialize CAS Ticket managemer
        super().__init__(auth=auth, config=config, db=backing, logger=logger)

        # protocol routes - CAS protocol spec specifies /cas prefix in API
        app.route('/cas/login', name="login", callback=self.cas_login, methods=['POST','GET'])
        app.route('/cas/logout', name="logout", callback=self.cas_logout)
        app.route('/cas/validate', name="validate", callback=self.cas_v1_validate)
        app.route(['/cas/serviceValidate', '/cas/p3/serviceValidate'], name="serviceValidate", callback=self.cas_v2_serviceValidate)
        app.route('/cas/samlValidate', callback=self.cas_v3_samlValidate_prox, method=['POST'])
        
        if self.cas_proxy_support:  # Enable proxy support
            app.route(['/cas/proxyValidate', '/cas/p3/proxyValidate'], name="proxyValidate", callback=self.cas_v2_proxyValidate)
            app.route('/cas/proxy', name="proxy", callback=self.cas_v2_proxy)
        else:   # Disable proxy support
            app.route(['/cas/proxyValidate', '/cas/p3/proxyValidate'], callback=self.notimplemented)
            app.route('/cas/proxy', callback=self.notimplemented)

        # niceness routes - go to login page
        app.route(['/cas/<anything>','/cas','/cas/'], name="anything", callback=self.default_route)


    # route: /cas/samlValidate - [POST] REST XML response
    def cas_v3_samlValidate_prox(self):
        """ Process V3 samlValidate """
        return cas_v3_samlValidate(self)

#
# CAS PROTOCOL ENDPOINTS
#
    # route: /cas/login - redirect or HTML response
    def cas_login(self, next=None, *args, **kwargs):
        """ CAS V1/v2/v3 login Require TGT or initiate auth login. """

        reauth = request.query.get('renew','false') == 'true'
        kwargs['force_reauth'] = reauth

        try:
            tg_ticket = self.lookup_granting_ticket(request.session.get(self.CAS_TGT))

        except Exception as e:
            tg_ticket = None

        if tg_ticket and not reauth:
            # good ticket - get to work
            return self.do_cas_login(tg_ticket) 

        else:
            # 'renew' or not authenticated - initiate login
            request.session[self.CAS_LOGGING_IN] = True

            # remove 'renew' from querystring
            qsdict = parse_qs(request.query_string)
            if 'renew' in qsdict: del qsdict['renew']

            ## rebuild URL
            url = request.url.split('?')[0]
            if qsdict: 
                url = url +  '?' + urlencode(qsdict,doseq=True)
            
            return self.auth.initiate_login(*args, next=url, **kwargs)


    # login real work
    def do_cas_login(self, tg_ticket):
        """ CAS V1/V2/V3 /cas/login - Return a Service Ticket. """

        service = request.query.get('service')

        if service:
            # Service Ticket is Requested
            service = unquote(service) + '?'
            service_base = service.split('?')[0]
            query_string = service.split('?')[1]

            if not self.service_list.valid(service_base):
                msg = f'Invalid service requested:  "{service_base}" is not authorized.'
                self.logger.info(f'CAS: {msg}')
                return CASResponse.auth_failure('INVALID_SERVICE', msg)
            
            # for 'renew' checks on serviceValidate
            creds_presented = request.session.get(self.FRESH_CREDENTIALS, False)
            request.session[self.FRESH_CREDENTIALS] = False

            # Issue service ticket and redirect to service.
            service_ticket = self.issue_ticket(tg_ticket, service_base, renewed=creds_presented)
            
            user = tg_ticket['username']
            self.logger.info(
                f'CAS: "{user}" issued service ticket {service_ticket} for "{service_base}"'
            )

            # redirect to service with ticket
            if query_string:
                url =  service_base + '?' + query_string + '&ticket=' + service_ticket
            else:
                url =  service_base + '?ticket=' + service_ticket
            
            return self.redirect(url)

        else:
            # no service ticket requested - render login acknowledge page
            return CASResponse.html(jinja2_template(
                'cas_loggedin.html',
                username = tg_ticket['username'],
                attrs = tg_ticket['details'],
                logouturl = self.app.get_url('logout')
                ))


    # route /cas/logout
    def cas_logout(self):
        """ CAS V1/V2/V3 /cas/logout. """

        tgt = request.session.get(self.CAS_TGT)
        username = request.session.get('USERNAME')
        
        if tgt:
            # remove any associated pgts
            self.destroy_pgts(username)
            # remove this tgt 
            self.db.delete(tgt)
            del request.session[self.CAS_TGT]

        # Log off ends our session
        request.session.session_delete()

        self.logger.info(f'CAS: user "{username}" logged out')
        
        # next URL for logout - redirect
        service = request.query.get('service')
        if service:
            service = unquote(service)
            return self.redirect(service)
        
        # Notification of log-off - required in CAS spec
        return CASResponse.html(jinja2_template(
                'cas_loggedout.html', 
                loginurl = self.app.get_url('login')
            ))


    # route: /cas/validate - REST text response
    def cas_v1_validate(self):
        """ CAS V1 /cas/validate - back-channel service ticket validation. """

        (status, reason, service_ticket) = self.validate_ticket(proxysok=False)
        
        if status == 'OK':
            # v1 success response is text 'yes' with the username on the second line
            msg = f'yes\n{service_ticket["username"]}\n'
        else:
            # v1 failure response is 'no'
            msg = 'no\n'
        
        return CASResponse.legacy_txt(msg)
            

    # /cas/{p3/}proxyValidate - REST XML/JSON response
    def cas_v2_proxyValidate(self):
        """ CAS V2/V3 /cas/{p3/}proxyValidate - backchannel service ticket validation. """
        
        # proxy validate shares code with serviceValidate - proxysok differentiates
        return self.cas_v2_serviceValidate(proxysok=self.cas_proxy_support)


    # /cas/{p3/}serviceValidate - REST XML/JSON response
    def cas_v2_serviceValidate(self, proxysok=False):
        """ CAS V2/V3 /cas/{p3/}serviceValidate - backchannel service ticket validation. """

        (status, reason, service_ticket) = self.validate_ticket(proxysok=proxysok)

        if status == 'OK':
            # Build reply with data from the service_ticket
            return CASResponse.auth_success(service_ticket)
        else:
            # Build error message
            return CASResponse.auth_failure(status, reason)


    # route: /cas/proxy - REST XML/JSON response
    def cas_v2_proxy(self):
        """ CAS V2/V3 /cas/proxy - Issue Proxy Ticket, return pgtiou. """

        target_service = request.query.get('targetService')
        pgt = request.query.get('pgt')
        error = None
        
        if not self.cas_proxy_support:
            error='INVALID_REQUEST'
            message='Proxy support disabled on this server.'
        
        elif pgt and target_service:
            # pgt and target_service are required parameters for /cas/proxy
            target_service = unquote(target_service)

            if not self.service_list.valid(target_service):
                # Service is not permitted
                error='INVALID_SERVICE'
                message = f'Invalid proxy service request {target_service}'

            elif not pgt.startswith('PGT-'):
                error='INVALID_TICKET'
                message=f'{pgt} is not a Proxy Grant Ticket'
            
            else:   
                # get the granting ticket detail
                pgt_ticket = self.lookup_proxy_granting_ticket(pgt)
                if pgt_ticket:
                    # PGT is valid - issue a pt for target_service       
                    proxy_ticket = self.issue_ticket(pgt_ticket, target_service, proxy=True)

                    user = pgt_ticket['username']
                    self.logger.info(f'CAS: "{user}" issued proxy ticket {proxy_ticket} for "{target_service}"')
                    
                    # return pt success
                    return CASResponse.proxy_success(proxy_ticket) 

                else:
                    # PGT is not found
                    error='INVALID_TICKET'
                    message=f'Proxy Grant Ticket {pgt} is Invalid.'
                    
        else:
            # Missing pgt or targetService
            error = 'INVALID_REQUEST'
            message='Both a pgt and targetService is required.'

        self.logger.info(f'CAS: Error "{error}" on Proxy request {request.url} : "{message}"')
        
        # return pt failure
        return CASResponse.proxy_failure(error, message)


    # route: /cas/<unimplemented> - any service configured out or not implemented
    def notimplemented(self):
        """ Unimplemented or Disabled Functionality """

        return 'Unimplemented'


    # route: /cas/<anything> => redirect to /cas/login
    def default_route(self, anything=None):
        """ Redirect nonsense back to the login page. """

        return self.redirect(self.app.get_url('login'))


    def redirect(self, url):
        """ Set response as 302 redirect """

        response.status = 302
        response.add_header('Cache-Control', 'no-store no-cache')
        response.add_header('Pragma', 'no-cache')
        response.add_header('Expires', '-1')
        response.set_header('Location', url)  
        return ''   # no response body in redirect
