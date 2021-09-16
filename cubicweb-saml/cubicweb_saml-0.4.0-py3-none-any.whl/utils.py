# copyright 2019-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__docformat__ = "restructuredtext en"

from random import randrange
from hashlib import sha512
from requests import get as requests_get

from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import Config
from saml2.entity import BINDING_HTTP_POST as ENTITY_BINDING_HTTP_POST

from cubicweb.server import DEBUG


def on_find_user(cnx, login, identity):
    """ Override this method to customize the find user behavior

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    login: str
        Login name from the SAML response
    identity: dict
        Special attributes as dictionary structure from the SAML response

    Returns
    -------
    int or None
        CWUser eid if an user was found, None otherwise
    """

    return find_user(cnx, login, identity)


def on_register_user(request):
    """ Override this method to customize the register user behavior

    Parameters
    ----------
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    int or None
        CWUser eid if the user has been correctly registered, None otherwise
    """

    return register_user(request)


def execute_rql(cnx, query, **kwargs):
    """ Quick method to execute a RQL query and retrieve the result if available

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    query : str
        RQL query
    kwargs : dict
        RQL arguments

    Returns
    -------
    Any or None
        RQL ResultSet first value if available, None otherwise

    See Also
    --------
    cubicweb.server.session.Connection.execute
    """

    rset = cnx.execute(query, kwargs)
    if rset:
        return rset[0][0]


def find_group_by_name(cnx, name):
    """ Retrieve a specific CWGroup from database

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    name : str
        CWGroup name to search inside the database

    Returns
    -------
    int or None
        CWGroup eid if the group has been found, None otherwise
    """

    return execute_rql(
        cnx, 'Any G WHERE G is CWGroup, G name %(name)s', name=name)


def find_user_by_login(cnx, login):
    """ Retrieve a specific CWUser from database

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    login : str
        CWUser name to search inside the database

    Returns
    -------
    int or None
        CWUser eid if the user has been found, None otherwise
    """

    return execute_rql(
        cnx, 'Any U WHERE U is CWUser, U login %(login)s', login=login)


def find_user(cnx, login, identity={}):
    """ Retrieve a specific user based on his login name and identity

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    login : str
        CWUser name to search inside the database
    identity : dict, default: empty
        SAML user information as dictionary structure

    Returns
    -------
    int or None
        CWUser eid if the user has been found, None otherwise
    """

    return find_user_by_login(cnx, login)


def get_user(request):
    """ Retrieve posted user informations from database

    Parameters
    ----------
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    int or None
        CWUser eid if the user has been found, None otherwise
    """

    login, identity = retrieve_informations_from_request(request)
    if login is None:
        return None

    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        return on_find_user(cnx, login, identity)


def register_user_into_db(cnx, login, group, password, identity={}):
    """ Register the user inside the database as a CWUser entity

    The specified password is only used to protect the CWUser account, since
    the connection will never ask for this password.

    Parameters
    ----------
    cnx: cubicweb.server.session.Connection
        CubiWeb session instance
    login : str
        The user name used as login
    group : str
        The group name where the user will be append
    password : str
        The hashed password used to protect the CWUser account
    identity : dict, default: empty
        SAML user information as dictionary structure

    Returns
    -------
    int or None
        CWUser eid if the user has been correctly registered, None otherwise
    """

    rset = execute_rql(cnx,
                       'INSERT CWUser U: U login %(login)s, '
                       '                 U upassword %(password)s, '
                       '                 U in_group G '
                       '           WHERE G name %(group)s',
                       login=str(login),
                       password=str(password),
                       group=group)
    cnx.commit()

    return rset


def register_user(request):
    """ Register an user inside the database

    Parameters
    ----------
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    int or None
        CWUser eid if the user has been correctly registered, None otherwise
    """

    login, identity = retrieve_informations_from_request(request)
    if login is None:
        return None

    config = request.registry['cubicweb.config']

    group = config.get('saml-register-default-group', 'guests')
    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        if not find_group_by_name(cnx, group):
            return None

    password = ''
    if config.get('saml-register-default-password', 'empty') == 'random':
        password = generate_hash(login)

    with request.registry['cubicweb.repository'].internal_cnx() as cnx:
        return register_user_into_db(cnx, login, group, password, identity)


def generate_hash(*args):
    """ Generate an hashed string based on specified arguments

    This method generate a string based on the specified arguments and a random
    number.

    Parameters
    ----------
    args : list
        String list used to generated the hashed string

    See Also
    --------
    hashlib.sha512
    """

    hash_value = sha512()

    for element in args:
        hash_value.update(str(element).encode('utf-8'))

    hash_value.update(
        str('{:06d}'.format(randrange(1, pow(10, 6)))).encode('utf-8'))

    return hash_value.hexdigest()


def get_metadata_from_uri(metadata_uri):
    """ Retrieve the metadata xml content from a specific URI

    Parameters
    ----------
    metadata_uri : str
        SAML metadata URI used to retrieve the metadata content

    Returns
    -------
    str
        Metadata content if available, an empty string is return otherwise

    See Also
    --------
    requests.get
    """

    if metadata_uri.startswith('file://'):
        with open(metadata_uri[7:], 'rb') as pipe:
            metadata = pipe.read()

        return metadata

    elif metadata_uri:
        return requests_get(metadata_uri).text

    return ''


def build_base_url(config):
    """ Generate base_url from cubicweb config

    This method ensure this URL ends with a slash.

    Parameters
    ----------
    config : cubicweb.pyramid.config.AllInOneConfiguration
        CubicWeb configuration instance

    Returns
    -------
    str
        CubicWeb base URL as registered in all-in-one.conf
    """

    base_url = config.get('base-url', '')
    if not base_url.endswith('/'):
        base_url += '/'

    return base_url


def saml_client(config):
    """ Generate a SAML client from all-in-one.conf metadata

    Parameters
    ----------
    config : cubicweb.pyramid.config.AllInOneConfiguration
        CubicWeb configuration instance

    Returns
    -------
    saml2.client.Saml2Client

    Raises
    ------
    KeyError
        If the saml section is missing from all-in-one.conf file
        If the saml-metadata-uri option is missing from all-in-one.conf file
    """
    cubicweb_sources = config.read_sources_file()

    if 'saml' not in cubicweb_sources:
        raise KeyError(
            "saml: Cannot found 'saml' section in cubicweb sources file")

    elif 'saml-metadata-uri' not in cubicweb_sources['saml']:
        raise KeyError(
            "saml: Cannot found 'saml-metadata-uri' option in saml section")

    base_url = build_base_url(config)

    settings = {
        'debug': bool(DEBUG),
        'entityid': cubicweb_sources['saml'].get('saml-entity-id', ''),
        'metadata': {
            'inline': [
                get_metadata_from_uri(
                    cubicweb_sources['saml']['saml-metadata-uri'])
            ],
        },
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (base_url + 'saml', BINDING_HTTP_POST),
                        (base_url + 'saml', BINDING_HTTP_REDIRECT),
                    ],
                },
                'allow_unsolicited':
                    config.get('saml-allow-unsolicited', True),
                'authn_requests_signed':
                    config.get('saml-authn-requests-signed', False),
                'logout_requests_signed':
                    config.get('saml-logout-requests-signed', True),
                'want_assertions_signed':
                    config.get('saml-want-assertions-signed', True),
                'want_response_signed':
                    config.get('saml-want-response-signed', False),
            },
        },
    }

    configuration = Config()
    configuration.allow_unknown_attributes = True
    configuration.load(settings)

    return Saml2Client(config=configuration)


def retrieve_informations_from_request(request):
    """ Retrieve SAML information from Pyramide request

    Parameters
    ----------
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    (str, dict) or (None, None)
        Login name and identity as dictionary structure if success, None's
        tuple otherwise
    """

    if request.POST and 'SAMLResponse' in request.POST:
        return retrieve_identity_from_client(
            request.registry['cubicweb.config'], request.POST['SAMLResponse'])

    return None, None


def retrieve_url_from_client(config, request):
    """ Generate SAML URL from metadata informations

    Parameters
    ----------
    config : cubicweb.pyramid.config.AllInOneConfiguration
        CubicWeb configuration instance
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    str
        SAML request URL if available, an empty string is return otherwise
    """

    reqid, info = saml_client(config).prepare_for_authenticate(
        relay_state=get_relay_state_from_request(config, request))

    # Select the IdP URL to send the AuthN request to
    return dict(info['headers']).get('Location', '')


def retrieve_identity_from_client(config, request):
    """ Retrieve identity from posted data

    Parameters
    ----------
    config : cubicweb.pyramid.config.AllInOneConfiguration
        CubicWeb configuration instance
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    (str, dict) or (None, dict)
        Login name and identity as dictionary structure if success, None
        tuple otherwise
    """

    authn_response = saml_client(config).parse_authn_request_response(
        request, ENTITY_BINDING_HTTP_POST)

    if authn_response:
        subject = authn_response.get_subject()
        if subject:
            subject = subject.text

        return subject, authn_response.get_identity()

    return None, {}


def get_relay_state_from_request(config, request):
    """ Generate relay state URL

    This method generate the location where the user should be returned after
    a successfull login.

    Parameters
    ----------
    config : cubicweb.pyramid.config.AllInOneConfiguration
        CubicWeb configuration instance
    request : pyramid.request.Request
        Pyramid request used to retrieve SAML response

    Returns
    -------
    str
        Relay state URL if available, an empty string is return otherwise
    """

    if request.GET:
        return request.GET.get('postlogin_path', '')

    elif request.POST:
        base_url = build_base_url(config)
        return request.POST.get('__errorurl', '').replace(base_url, '')

    return ''
