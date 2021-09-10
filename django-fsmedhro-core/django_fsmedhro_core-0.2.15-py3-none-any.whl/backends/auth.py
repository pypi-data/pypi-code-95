import logging
from ldap3 import Server, Connection, ALL_ATTRIBUTES
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import messages

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class LDAPUniRostock:
    HOST = 'ldaps://ldap.uni-rostock.de'
    BASE_DN = 'ou=people,o=uni-rostock,c=de'
    server = Server(HOST)

    def authenticate(self, request, username, password):
        username = username.lower()
        uid_qualifier = f'uid={username}'
        user_dn = f'{uid_qualifier},{self.BASE_DN}'

        logger.debug(f'Trying to authenticate with user_dn: {user_dn}')
        conn = Connection(self.server, user_dn, password)

        """
        Für die Authentifizierung versuchen wir uns hier an den LDAP-Server
        zu binden. Wenn es hierbei keine Exception gibt, dann ist der
        Benutzer gültig.
        """
        bind_successful = conn.bind()

        if bind_successful:
            """
            Wenn wir uns erfolgreich binden konnten, dann holen wir uns vom
            LDAP-Server alle Informationen um unseren eigenen Nutzer zu
            befüllen.
            """
            uid_search_term = f'({uid_qualifier})'
            conn.search(
                self.BASE_DN,
                uid_search_term,
                attributes=ALL_ATTRIBUTES
            )
            ldap_user = conn.entries[0]
            logger.debug(f'Got LDAP User: {ldap_user}')
        else:
            logger.debug('Could not authenticate. Unsuccessful bind.')
            messages.warning(
                request,
                'Authentifizierung bei der Uni fehlgeschlagen – '
                'bitte überprüfe dein Kürzel und Passwort.'
            )
            return None

        conn.unbind()

        if self.is_valid(ldap_user):
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                """
                Wenn der Benutzer noch nicht existiert, dann erstellen wir
                einen:
                """
                user = UserModel(
                    username=ldap_user.uid.value,
                    password='DummyPassword',
                    is_staff=False,
                    is_superuser=False,
                )

                user.set_unusable_password()

                user.save()

            if user.is_active:
                user.email = ldap_user.mail.value
                user.first_name = ldap_user.givenName.value
                user.last_name = ldap_user.sn.value

                user.save()

            return user
        else:
            messages.warning(
                request,
                "Zutritt gibt's leider nur für Studenten "
                "der medizinischen Fakultät."
            )
            return None

    def is_valid(self, ldap_user):
        """
        Es werden nur Studenten von der Medizinischen Fakultät akzeptiert,
        außer die Accounts mit Ausnahmeregelungen in
        settings.FSRMED_AUTH_EXCEPTIONS.
        """
        try:
            logger.debug(
                f'Current auth exceptions: {settings.FSRMED_AUTH_EXCEPTIONS}'
            )
            if ldap_user.uid.value in settings.FSRMED_AUTH_EXCEPTIONS:
                return True
        except AttributeError:
            pass

        ldap_auth_filter = {
            'employeeType': {'s', 'si'},
            'uniRFaculty': {'03'},
            'gidNumber': {97},
        }

        """
        Es wird jedes Filterkriterium auf Gültigkeit überprüft.
        Der Wert vom ldap_user für die relevanten Schlüssel aus ldap_auth_filter muss
        in den dazugehörigen Werten aus ldap_auth_filter vorkommen.
        """
        for key, target_values in ldap_auth_filter.items():
            v = ldap_user[key].value
            invalid_user_warning_msg = (
                f'Invalid user {ldap_user.uid} because of {key} '
                f'(should be in {target_values} but is {v})'
            )

            if type(v) == int:
                vs = {v}
            elif type(v) == str:
                # Es könnte sein, dass ';' die verschiedenen employeeTypes trennt.
                vs = set(v.split(';'))
            else:
                vs = set(v)

            """
            Die Daten vom User müssen in allen Punkten mind. eine Übereinstimmung
            mit den Zieldaten haben, also z.B. wenn der Nutzer den employeeType
            'mi;si' hat (deswegen der split oben), dann soll der Nutzer sich einloggen
            können.
            """
            if not vs & target_values:
                logger.warning(invalid_user_warning_msg)
                return False
        else:
            return True

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
