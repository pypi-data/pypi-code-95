import datetime
from .models import UserKey
from .constants import USER_PK_SESSION_KEY, USER_AUTH_BACKEND


def has_mfa(request, user):
    """Check if MFA is enabled for this user
    If yes, return all keys (which may be useful to redirect or show user options)
    In addition, mark session with user pk to mark successful initial factor login
    If no, return False (in which case, log in normally)
    """
    mfa_types = [UserKey.KeyType.FIDO2, UserKey.KeyType.TOTP]
    user_keys = user.userkey_set.filter(key_type__in=mfa_types)
    if user_keys.exists():
        # Mark session as successful step 1 authentication
        set_expirable_var(request.session, USER_PK_SESSION_KEY, user.pk)
        # Remember auth backend, needed to call django login function when multiple backends are used.
        set_expirable_var(request.session, USER_AUTH_BACKEND, user.backend)
        return user_keys
    return False


def set_expirable_var(session, var_name, value, expire_at=None):
    """Set session variable with expiration, expire_at defaults to 5 minutes."""
    if expire_at is None:
        expire_at = datetime.datetime.today() + datetime.timedelta(minutes=5)
    session[var_name] = {"value": value, "expire_at": expire_at.timestamp()}


def get_expirable_var(session, var_name, default=None):
    var = default
    if var_name in session:
        my_variable_dict = session.get(var_name, {})
        if my_variable_dict.get("expire_at", 0) > datetime.datetime.now().timestamp():
            return my_variable_dict.get("value")
        else:
            del session[var_name]
    return var
