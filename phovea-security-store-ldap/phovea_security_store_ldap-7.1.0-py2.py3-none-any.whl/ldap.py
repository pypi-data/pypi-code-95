import logging
import ldap3
import phovea_server.security
from ldap3.core.exceptions import LDAPInvalidCredentialsResult

__author__ = 'Samuel Gratzl'
log = None


def cleanup_name(username):
  if '\\' in username:
    return username[username.index('\\') + 1:]
  if '@' in username:
    return username[0:username.index('@')]
  return username


def cleanup_group(group):
  if (type(group) is list or type(group) is tuple) and len(group) == 1:
    return str(group[0])
  return str(group)


class LDAPUser(phovea_server.security.User):
  """
  a simple unix user backend with the file permissions
  """

  def __init__(self, username, dn=None, info=None, groups=None, group_prop='dn'):
    super(LDAPUser, self).__init__(dn or username)
    self.name = cleanup_name(username)
    self.groups = groups or []
    if group_prop is not None:
      self.roles = [cleanup_group(g[group_prop]) for g in self.groups]
    else:
      self.roles = [str(g) for g in self.groups]
    self.dn = dn or username
    self.info = info or {}

  @property
  def is_authenticated(self):
    return True

  @property
  def is_active(self):
    return True


# inspired by flask-ldap3-login https://github.com/nickw444/flask-ldap3-login

class LDAPStore(object):
  def __init__(self):
    import atexit
    from phovea_server.config import view as configview
    self._config = configview('phovea_security_store_ldap')

    # cached of logged in user objects
    self._cache = dict()

    self._server_pool = ldap3.ServerPool([], ldap3.FIRST, active=True, exhaust=True)
    self._connection = None

    for server_c in self._config.servers:
      server = ldap3.Server(server_c['hostname'], port=int(server_c['port']),
                            use_ssl=bool(server_c.get('use_ssl', False)))
      self._server_pool.add(server)

    atexit.register(self.__del__)

  def _make_connection(self, bind_user=None, bind_password=None, **kwargs):
    """
    Make a connection.

    Args:
        bind_user (str): User to bind with. If `None`, AUTH_ANONYMOUS is
            used, otherwise authentication specified with
            config['LDAP_BIND_AUTHENTICATION_TYPE'] is used.
        bind_password (str): Password to bind to the directory with
        contextualise (bool): If true (default), will add this connection to the
            appcontext so it can be unbound upon app_teardown.

    Returns:
        ldap3.Connection: An unbound ldap3.Connection. You should handle exceptions
            upon bind if you use this internal method.
    """

    authentication = ldap3.ANONYMOUS
    if bind_user:
      # prepend default domain if available
      if '\\' not in bind_user and '@' not in bind_user and self._config.default_netbios_domain != '':
        bind_user = self._config.default_netbios_domain + '\\' + bind_user
      authentication = getattr(ldap3, self._config.bind_authentification_type)

    log.debug('Opening connection with bind user "{0}"'.format(bind_user or 'Anonymous'))
    connection = ldap3.Connection(server=self._server_pool, read_only=self._config.read_only, user=bind_user,
                                  password=bind_password, client_strategy=ldap3.SYNC,
                                  authentication=authentication, check_names=True, raise_exceptions=True, **kwargs)
    return connection

  def __del__(self):
    if self._connection:
      self._connection.unbind()
      self._connection = None
    pass

  @property
  def connection(self):
    if self._connection is None:
      self._connection = self._make_connection(self._config.bind_user_dn, self._config.bind_user_password)
      self._connection.bind()
    return self._connection

  def logout(self, user):
    if self._config.cache and hasattr(user, 'id'):
      del self._cache[user.id]
    pass

  def load(self, id):
    if self._config.cache:
      return self._cache.get(id, None)
    return self._refind_user(id)

  def load_from_key(self, api_key):
    parts = api_key.split(':')
    if len(parts) != 2:
      return None
    return self.login(parts[0], dict(password=parts[1]))

  def login(self, username, extra_fields=None):
    # Check if user is blacklisted
    if username and username.lower() in self._config.get('blacklist', default=[]):
      log.info(f'unsuccessful login for blacklisted user {username}')
      return None

    if extra_fields is None:
      extra_fields = {}
    password = extra_fields['password']
    method = self._config.method
    if method == 'bind_direct':
      result = self._authenticate_direct_credentials(username, password)
    elif method == 'bind_direct_and_search':
      result = self._authenticate_direct_bind_and_search(username, password)
    elif method == 'bind_guess_cn':
      # Since the user's RDN is the same as the login field,
      # we can do a direct bind.
      result = self._authenticate_direct_bind(username, password)
    else:
      # We need to search the User's DN to find who the user is (and their DN)
      # so we can try bind with their password.
      result = self._authenticate_search_bind(username, password)

    if result and self._config.user['required_groups'] and not all(result.has_role(r) for r in self._config.user['required_groups']):
      log.info('successful login for %s %s but not in required groups %s', result.name, str(result.roles), self._config.user['required_groups'])
      return None

    if result and self._config.cache:
      self._cache[result.id] = result
    return result

  def _authenticate_direct_credentials(self, username, password):
    """
    Performs a direct bind, however using direct credentials. Can be used if
    interfacing with an Active Directory domain controller which
    authenticates using username@domain.com directly.

    Performing this kind of lookup limits the information we can get from
    ldap. Instead we can only deduce whether or not their bind was
    successful. Do not use this method if you require more user info.

    Args:
        username (str): fully qualified username for the user to bind with.
        password (str): User's password to bind with.

    Returns:
        AuthenticationResponse
    """

    connection = self._make_connection(bind_user=username, bind_password=password)

    try:
      connection.bind()
      log.debug('Authentication was successful for user "{0}"'.format(username))
      return LDAPUser(username)
    except LDAPInvalidCredentialsResult:
      log.debug('Authentication was not successful for user "{0}"'.format(username))
      return None
    except Exception:
      log.exception('unknown exception')
      return None
    finally:
      connection.unbind()

  def _authenticate_direct_bind(self, username, password):
    """
    Performs a direct bind. We can do this since the RDN is the same
    as the login attribute. Hence we just string together a dn to find
    this user with.

    Args:
        username (str): Username of the user to bind (the field specified
            as LDAP_BIND_RDN_ATTR)
        password (str): User's password to bind with.

    Returns:
        AuthenticationResponse
    """

    bind_user = '{rdn}={username},{user_search_dn}'.format(rdn=self._config.get('user.rdn_attr'), username=username,
                                                           user_search_dn=self.full_user_search_dn)

    connection = self._make_connection(bind_user, password)

    try:
      connection.bind()
      log.debug('Authentication was successful for user "{0}"'.format(username))

      # Get user info here.

      user_info = self._get_user_info(dn=bind_user, _connection=connection)
      user_groups = self._get_user_groups(dn=bind_user, _connection=self._choose(connection))

      return LDAPUser(username, info=user_info, groups=user_groups, dn=bind_user,
                      group_prop=self._config.get('group.prop'))
    except LDAPInvalidCredentialsResult:
      log.debug('Authentication was not successful for user "{0}"'.format(username))
      return None
    except Exception:
      log.exception('unknown exception')
      return None
    finally:
      connection.unbind()

  def _authenticate_direct_bind_and_search(self, username, password):
    """
    Performs a direct bind. We can do this since the RDN is the same
    as the login attribute. Hence we just string together a dn to find
    this user with.

    Args:
        username (str): Username of the user to bind (the field specified
            as LDAP_BIND_RDN_ATTR)
        password (str): User's password to bind with.

    Returns:
        AuthenticationResponse
    """
    import re
    import json

    connection = self._make_connection(username, password)

    try:
      log.debug('start binding')
      connection.bind()
      log.debug('Authentication was successful for user "{0}"'.format(username))

      if self._config.get('use_who_am_i'):
        # Luckily there's an LDAP standard operation to help us out
        my_username = connection.extend.standard.who_am_i()
        log.debug('who_am_i(): %r', my_username)
        # ignore ts lint error, the fix would break the login mechanism
        my_username = re.sub('^u:\w+\\\\', '', my_username)  # noqa: W605
        log.debug('re.sub: %r', my_username)
      else:
        my_username = username

      # Get user info here.
      # Find the user in the search path.
      user_filter = '({search_attr}={username})'.format(search_attr=self._config.get('user.login_attr'),
                                                        username=my_username)
      log.debug("user_filter(before): %r", user_filter)

      if self._config.get('user.alternative_login_attr') is not None:
        user_filter = '(|{first}({search_attr}={username}))'.format(first=user_filter, search_attr=self._config.get('user.alternative_login_attr'), username=my_username)
        log.debug("user_filter(after): %r", user_filter)

      search_filter = '(&{0}{1})'.format(self._config.get('user.object_filter'), user_filter)
      log.debug("search_filter: %r", search_filter)

      search_filter = '(&{0}{1})'.format(self._config.get('user.object_filter'), user_filter)
      log.debug('search_filter: %r', search_filter)

      log.debug('Performing an LDAP Search using filter "{0}", ''base "{1}", and scope "{2}"'.format(search_filter, self.full_user_search_dn, self._config.get('user.search_scope')))

      connection.search(search_base=self.full_user_search_dn, search_filter=search_filter,
                        search_scope=getattr(ldap3, self._config.get('user.search_scope')),
                        attributes=self._config.get('user.attributes') or ldap3.ALL_ATTRIBUTES)

      if len(connection.response) > 0:
        first_entry = json.loads(connection.response_to_json())['entries'][0]
        user_info = first_entry['attributes']
        user_info['dn'] = first_entry['dn']
        bind_user = user_info['dn']
      else:
        raise Exception

      if len(connection.response) > 0 and 'memberOf' in json.loads(connection.response_to_json())['entries'][0]['attributes']:
        user_groups = json.loads(connection.response_to_json())['entries'][0]['attributes'].get('memberOf', [])
      else:
        user_groups = self._get_user_groups(dn=bind_user, _connection=self._choose(connection))

      return LDAPUser(my_username, info=user_info, groups=user_groups, dn=bind_user,
                      group_prop=self._config.get('group.prop'))
    except LDAPInvalidCredentialsResult:
      log.exception('Authentication was not successful for user "{0}"'.format(username))
      return None
    except Exception:
      log.exception('Cannot find user "{0}" full dn'.format(username))
      return None
    finally:
      connection.unbind()

  def _authenticate_search_bind(self, username, password):
    """
    Performs a search bind to authenticate a user. This is
    required when a the login attribute is not the same
    as the RDN, since we cannot string together their DN on
    the fly, instead we have to find it in the LDAP, then attempt
    to bind with their credentials.

    Args:
        username (str): Username of the user to bind (the field specified
            as LDAP_BIND_LOGIN_ATTR)
        password (str): User's password to bind with when we find their dn.

    Returns:
        AuthenticationResponse
    """
    connection = self._make_connection(bind_user=self._config.get('bind_user_dn'),
                                       bind_password=self._config.get('bind_user_password'))

    try:
      connection.bind()
      log.debug('Successfully bound to LDAP as "{0}" for search_bind method'.format(self._config.get('bind_user_dn') or 'Anonymous'))
    except Exception:
      connection.unbind()
      log.exception('unknown')
      return None

    # Find the user in the search path.
    user_filter = '({0}={1})'.format(self._config.get('user.login_attr'), username)
    search_filter = '(&{0}{1})'.format(self._config.get('user.object_filter'), user_filter)

    log.debug('Performing an LDAP Search using filter "{0}", base "{1}", and scope "{2}"'.format(search_filter, self.full_user_search_dn, self._config.get('user.search_scope')))

    connection.search(search_base=self.full_user_search_dn, search_filter=search_filter,
                      search_scope=getattr(ldap3, self._config.get('user.search_scope')),
                      attributes=self._config.get('user.attributes') or ldap3.ALL_ATTRIBUTES)
    user_obj = None
    rlen = len(connection.response)
    if rlen == 0 or (self._config.get('fail_auth_on_multiple_found') and rlen > 1):
      # Don't allow them to log in.
      log.debug('Authentication was not successful for user "{0}"'.format(username))
    else:
      for user in connection.response:
        # Attempt to bind with each user we find until we can find
        # one that works.
        user_connection = self._make_connection(bind_user=user['dn'], bind_password=password)

        log.debug('Directly binding a connection to a server with user:"{0}"'.format(user['dn']))
        try:
          user_connection.bind()
          log.debug('Authentication was successful for user "{0}"'.format(username))

          # Populate User Data
          user['attributes']['dn'] = user['dn']
          groups = self._get_user_groups(dn=user['dn'], _connection=user_connection if self._config.get('resolve_objects') == 'user' else connection)
          user_obj = LDAPUser(username, dn=user['dn'], info=user['attributes'], groups=groups,
                              group_prop=self._config.get('group.prop'))
          break
        except LDAPInvalidCredentialsResult:
          log.exception('Authentication was not successful for user "{0}"'.format(username))
        except Exception:  # pragma: no cover
          # This should never happen, however in case ldap3 does ever throw an error here,
          # we catch it and log it
          log.exception('unknown')
        finally:
          user_connection.unbind()

    connection.unbind()
    return user_obj

  def _refind_user(self, dn):
    connection = self._make_connection(bind_user=self._config.get('bind_user_dn'),
                                       bind_password=self._config.get('bind_user_password'))

    try:
      connection.bind()
      log.debug('Successfully bound to LDAP as "{0}" for search_bind method'.format(self._config.get('bind_user_dn') or 'Anonymous'))
      infos = self._get_user_info(dn, _connection=self._choose(connection))
      groups = self._get_user_groups(dn, _connection=self._choose(connection))
      return LDAPUser(infos.get('name', infos.get('cn', dn)), dn=dn, info=infos, groups=groups, group_prop=self._config.get('group.prop', default='dn'))
    except Exception:
      log.exception('unknown')
      return None
    finally:
      connection.unbind()

  def _choose(self, connection):
    return connection if self._config.get('resolve_objects') == 'user' else None

  def _get_user_groups(self, dn, group_search_dn=None, _connection=None):
    """
    Gets a list of groups a user at dn is a member of

    Args:
        dn (str): The dn of the user to find memberships for.
        _connection (ldap3.Connection): A connection object to use when
            searching. If not given, a temporary connection will be
            created, and destroyed after use.
        group_search_dn (str): The search dn for groups. Defaults to
            ``'{LDAP_GROUP_DN},{LDAP_BASE_DN}'``.

    Returns:
        list: A list of LDAP groups the user is a member of.
    """

    connection = _connection
    if not connection:
      connection = self._make_connection(bind_user=self._config.get('bind_user_dn'),
                                         bind_password=self._config.get('bind_user_password'))
      connection.bind()

    # use paged_search to avoid artificial cut off
    s = connection.extend.standard

    filter_manually = self._config.get('group.filter_manually')
    if filter_manually:
      search_filter = self._config.get('group.object_filter')
    else:
      search_filter = '(&{0}({1}={2}))'.format(self._config.get('group.object_filter'),
                                               self._config.get('group.members_attr'), dn)

    log.debug('Searching for groups for specific user with filter "{0}" , base "{1}" and scope "{2}"'.format(search_filter, group_search_dn or self.full_group_search_dn, self._config.get('group.search_scope')))

    item_gen = s.paged_search(search_base=group_search_dn or self.full_group_search_dn,
                              search_filter=search_filter,
                              attributes=self._config.get('group.attributes') or ldap3.ALL_ATTRIBUTES,
                              search_scope=getattr(ldap3, self._config.get('group.search_scope')),
                              paged_size=16,
                              generator=True)

    results = []

    for item in item_gen:
      group_data = item['attributes']
      group_data['dn'] = item['dn']
      if not filter_manually or dn in group_data.get(self._config.get('group.members_attr'), []):
        results.append(group_data)

    if not _connection:
      # We made a connection, so we need to kill it.
      connection.unbind()

    match = self._config.get('group.match')
    if match is not None:
      import re
      match = re.compile(match)
      results = [r for r in list(results) if match.match(r['dn'])]

    return results

  def _get_user_info(self, dn, _connection=None):
    """
    Gets info about a user specified at dn.

    Args:
        dn (str): The dn of the user to find
        _connection (ldap3.Connection): A connection object to use when
            searching. If not given, a temporary connection will be
            created, and destroyed after use.

    Returns:
        dict: A dictionary of the user info from LDAP

    """
    return self._get_object(dn=dn, filter=self._config.get('user.object_filter'),
                            attributes=self._config.get('user.attributes') or ldap3.ALL_ATTRIBUTES,
                            _connection=_connection)

  def _get_user_info_for_username(self, username, _connection=None):
    """
    Gets info about a user at a specified username by searching the
    Users DN. Username attribute is the same as specified as
    LDAP_USER_LOGIN_ATTR.


    Args:
        username (str): Username of the user to search for.
        _connection (ldap3.Connection): A connection object to use when
            searching. If not given, a temporary connection will be
            created, and destroyed after use.
    Returns:
        dict: A dictionary of the user info from LDAP
    """
    ldap_filter = '(&({0}={1}){2})'.format(self._config.get('user.login_attr'), username,
                                           self._config.get('user.object_filter'))

    return self._get_object(dn=self.full_user_search_dn, filter=ldap_filter,
                            attributes=self._config.get('user.attributes') or ldap3.ALL_ATTRIBUTES,
                            _connection=_connection)

  def _get_group_info(self, dn, _connection=None):
    """
    Gets info about a group specified at dn.

    Args:
        dn (str): The dn of the group to find
        _connection (ldap3.Connection): A connection object to use when
            searching. If not given, a temporary connection will be
            created, and destroyed after use.

    Returns:
        dict: A dictionary of the group info from LDAP
    """

    return self._get_object(dn=dn, filter=self._config.get('group.object_filter'),
                            attributes=self._config.get('group.attributes') or ldap3.ALL_ATTRIBUTES,
                            _connection=_connection)

  def _get_object(self, dn, filter, attributes, _connection=None):
    """
    Gets an object at the specified dn and returns it.

    Args:
        dn (str): The dn of the object to find.
        filter (str): The LDAP syntax search filter.
        attributes (list): A list of LDAP attributes to get when searching.
        _connection (ldap3.Connection): A connection object to use when
            searching. If not given, a temporary connection will be created,
            and destroyed after use.

    Returns:
        dict: A dictionary of the object info from LDAP
    """
    import json

    connection = _connection
    if not connection:
      connection = self._make_connection(bind_user=self._config.get('bind_user_dn'),
                                         bind_password=self._config.get('bind_user_password')
                                         )
      connection.bind()

    connection.search(search_base=dn, search_filter=filter, attributes=attributes)

    data = None
    if len(connection.response) > 0:
      first_entry = json.loads(connection.response_to_json())['entries'][0]
      data = first_entry['attributes']
      data['dn'] = first_entry['dn']

    if not _connection:
      # We made a connection, so we need to kill it.
      connection.unbind()
    return data

  @property
  def full_user_search_dn(self):
    """
    Returns a the base search DN with the user search DN prepended.

    Returns:
        str: Full user search dn
    """
    return self.compiled_sub_dn(self._config.get('user_dn'))

  @property
  def full_group_search_dn(self):
    """
    Returns a the base search DN with the group search DN prepended.

    Returns:
        str: Full group search dn
    """
    return self.compiled_sub_dn(self._config.get('group_dn'))

  def compiled_sub_dn(self, prepend):
    """
    Returns:
        str: A DN with the DN Base appended to the end.

    Args:
        prepend (str): The dn to prepend to the base.
    """
    prepend = prepend.strip()
    if prepend == '':
      return self._config.get('base_dn')
    return '{prepend},{base}'.format(prepend=prepend, base=self._config.get('base_dn'))


def create():
  # recreate log
  global log
  log = logging.getLogger(__name__)
  return LDAPStore()
