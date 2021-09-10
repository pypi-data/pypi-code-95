import cacahuate.auth.base
import cacahuate.errors
import cacahuate.models

import ldap3
import ldap3.core.exceptions


class LdapAuthProvider(cacahuate.auth.base.BaseAuthProvider):
    def authenticate(self, **credentials):
        if 'username' not in credentials or not credentials['username']:
            raise cacahuate.errors.AuthFieldRequired('username')
        if 'password' not in credentials or not credentials['password']:
            raise cacahuate.errors.AuthFieldRequired('password')

        server_uri = self.config['AUTH_LDAP_SERVER_URI']
        use_ssl = self.config['AUTH_LDAP_USE_SSL']
        domain = self.config['AUTH_LDAP_DOMAIN']
        search_base = self.config['AUTH_LDAP_SEARCH_BASE']
        search_filter = self.config['AUTH_LDAP_SEARCH_FILTER']

        # Use credentials to authenticate
        username = credentials['username'].lower()
        password = credentials['password']
        if 'domain' in credentials:
            domain = credentials['domain']

        # Connect & query ldap
        server = ldap3.Server(
            server_uri,
            get_info=ldap3.ALL,
            use_ssl=use_ssl,
        )

        try:
            conn = ldap3.Connection(
                server,
                user='{}\\{}'.format(domain, username),
                password=password,
                auto_bind=True,
            )
        except ldap3.core.exceptions.LDAPBindError:
            raise cacahuate.errors.AuthFieldInvalid('password')
        except ldap3.core.exceptions.LDAPSocketOpenError:
            raise cacahuate.errors.MisconfiguredProvider(
                f'Can\'t reach {server_uri}',
            )

        conn.search(
            search_base,
            search_filter.format(user=username),
            attributes=list(self.config['AUTH_LDAP_USER_ATTR_MAP'].values()),
        )

        try:
            entry = conn.entries[0]
        except IndexError:
            raise cacahuate.errors.AuthFieldInvalid('username')

        identifier = '{domain}\\{username}'.format(
            domain=domain,
            username=username,
        )

        user = cacahuate.models.get_or_create_user(
            identifier,
            {
                k: getattr(entry, v)
                for k, v in self.config['AUTH_LDAP_USER_ATTR_MAP'].items()
            },
        )

        # update if required
        for k, v in self.config['AUTH_LDAP_USER_ATTR_MAP'].items():
            setattr(user, k, getattr(entry, v))
        user.save()

        return (identifier, {
            'identifier': user.identifier,
            'email': user.email,
            'fullname': user.fullname,
        })
