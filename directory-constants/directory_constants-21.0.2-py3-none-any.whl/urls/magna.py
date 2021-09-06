from directory_constants.helpers import get_url


# SERVICES
HOME = get_url('DIRECTORY_CONSTANTS_URL_GREAT_MAGNA', 'https://www.great.gov.uk')
INTERNATIONAL = HOME / 'international'


# Header links
LEARN = HOME / 'learn'
WHERE_TO_EXPORT = HOME / 'where-to-export'
LEARN_TO_EXPORT = LEARN / 'categories'

EXPORT_PLAN = HOME / 'export-plan'
EXPORT_PLAN_DASHBOARD = EXPORT_PLAN / 'dashboard'

ADVICE = HOME / 'advice'
ACCOUNT = HOME / 'profile'
MARKETS = HOME / 'markets'

SEARCH = HOME / 'search'
MARKETS = HOME / 'markets'
GET_FINANCE = HOME / 'get-finance'
GREAT_DOMESTIC_NEWS = HOME / 'news'
SERVICES = HOME / 'services'
ABOUT = HOME / 'about'
COOKIE_PREFERENCE_SETTINGS = HOME / 'cookies'

# footer links
CONTACT_US = HOME / 'contact'
CONTACT_US_HELP = CONTACT_US / 'help'
PRIVACY_AND_COOKIES = HOME / 'privacy-and-cookies'
TERMS_AND_CONDITIONS = HOME / 'terms-and-conditions'
ACCESSIBILITY = HOME / 'accessibility-statement'
PERFORMANCE_DASHBOARD = HOME / 'performance-dashboard'
DIT = 'https://www.gov.uk/government/organisations/department-for-international-trade'
