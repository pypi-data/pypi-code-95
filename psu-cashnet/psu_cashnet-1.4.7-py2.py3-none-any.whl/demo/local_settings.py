# ###############################################################
# THESE SECRET VALUES MUST BE PROVIDED:
# (this file will be ignored by Git)

FINTI_TOKEN = "2144402c-586e-44fc-bd0c-62b31e98394d"
EMAIL_HOST_PASSWORD = 'EuDFxamEfm7y'

assert(FINTI_TOKEN is not None, 'You MUST provide a Finti token')
# ###############################################################


# Environment choices: {DEV, TEST, PROD}
ENVIRONMENT = 'DEV'

# SECURITY WARNING: Change this and keep it a secret in production!
SECRET_KEY = 'j3y0jmakw)%#bm!**34kw3et63o@&+zlj82(72qq%6c^y)e&8$'

# Name of machine running the application
ALLOWED_HOSTS = ['localhost']

# Debug mode (probably only true in DEV)
DEBUG = True

# SSO URL
CAS_SERVER_URL = 'https://sso-stage.oit.pdx.edu/idp/profile/cas/login'

# `````````````````
# FINTI
# `````````````````
# REQUIRED: Finti URL and Token:

FINTI_URL = 'https://ws-dev.oit.pdx.edu'

# Finti URLs (for reference)
# -  http://localhost:8888
# -  https://ws-test.oit.pdx.edu
# -  https://ws.oit.pdx.edu

# As-of psu-base 0.11.0, Finti responses can be cached for offline development
FINTI_SIMULATE_WHEN_POSSIBLE = True   # Simulate Finti calls (i.e. when not on VPN)
FINTI_SAVE_RESPONSES = True    # Save/record actual Finti responses for offline use?

EMAIL_HOST_USER = 'cefr-app-mail'


# -----------------------------------------------------------------------------
# OPTIONAL VALUES
# -----------------------------------------------------------------------------

# You may want to disable elevated developer access while running locally
# ELEVATE_DEVELOPER_ACCESS = False

# You may want to extend session expiration during local development
# SESSION_COOKIE_AGE = 4 * 60 * 60  # 4 hours
