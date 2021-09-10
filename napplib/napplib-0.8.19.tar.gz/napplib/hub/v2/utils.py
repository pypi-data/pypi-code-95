# build-in imports
from enum import Enum


class Environment(Enum):
	STAGING		= 'https://dev-api-int-hub.nappsolutions.io/v2'
	PRODUCTION 	= 'https://api-int-hub.nappsolutions.io/v2'
	DEVELOPMENT	= 'http://localhost:9090/v2'
