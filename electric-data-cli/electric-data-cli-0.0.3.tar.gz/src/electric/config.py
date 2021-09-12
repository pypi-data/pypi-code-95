"""Application config."""

import os
env = os.environ

def default_endpoint():
    return env.get('ELECTRIC_DATA_DEFAULT_ENDPOINT', 'https://api.electricdata.net')

def documentation_url():
    return env.get('ELECTRIC_DATA_DOCUMENTATION_URL', 'https://electricdata.net/docs')

def is_testing():
    return bool(env.get('ELECTRIC_DATA_IS_TESTING', False))

def should_open_browser():
    return bool(env.get('ELECTRIC_DATA_OPEN_BROWSER', False))
