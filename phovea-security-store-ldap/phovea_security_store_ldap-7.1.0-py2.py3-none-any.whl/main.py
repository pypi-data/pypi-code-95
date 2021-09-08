def create(_):
  def _loop():
    from .ldap import LDAPStore, log
    import logging
    import getpass

    log.setLevel(logging.DEBUG)
    store = LDAPStore()
    username = input('username: ')

    while username:
      password = getpass.getpass('password: ')
      user = store.login(username, dict(password=password))
      if user:
        print(('OK {u.id} name:{u.name} roles:{u.roles} dn:{u.dn} {u.info} {u.groups}'.format(u=user)))
      else:
        print('ERROR')
      username = input('another username: ')

  return lambda _: _loop
