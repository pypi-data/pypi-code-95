import os

from .. import context as base_context

__DOMINO_TOKEN_FILE_ENV = 'DOMINO_TOKEN_FILE'
__DOMINO_DEFAULT_USER_CLAIM = 'preferred_username'

def token_func():
    if __DOMINO_TOKEN_FILE_ENV not in os.environ:
        raise Exception('Could not find Domino token environment variable: %s' % (
            __DOMINO_TOKEN_FILE_ENV))

    token_path = os.environ[__DOMINO_TOKEN_FILE_ENV]
    if not os.path.exists(token_path):
        raise Exception('Could not find Domino token file at "%s"' % token_path)

    return open(token_path, 'r').read().strip()

def context(*args, user_claims=None, **kwargs):
    """ Gets a pyokera context object configured for Domino Data Labs environments.

        Parameters
        ----------
        user_claims : list of str, optional
            Optional list of claims to extract user from token

    Returns
    -------
    OkeraContext
        Context object.

    Examples
    --------
    >>> from okera.integration import domino
    >>> ctx = domino.context()
    >>> with ctx.connect(host = 'okera.company.com', port = 12050) as conn:
    ...     result = conn.execute_ddl('select * from okera_sample.whoami')
    ...     result
    [{'user': '<domino user>'}]
    """
    # If there was no explicit user_claims set, we use the default one for
    # Domino
    if not user_claims:
        user_claims = [__DOMINO_DEFAULT_USER_CLAIM]
    ctx = base_context(*args, **kwargs)
    ctx.enable_token_auth(token_func=token_func, user_claims=user_claims)

    return ctx
