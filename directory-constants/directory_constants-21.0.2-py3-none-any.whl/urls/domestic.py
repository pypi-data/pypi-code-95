from directory_constants.helpers import get_url


# SERVICES
HOME = get_url('DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC', 'https://www.great.gov.uk')
EVENTS = get_url('DIRECTORY_CONSTANTS_URL_EVENTS', 'https://www.events.great.gov.uk')
SELLING_OVERSEAS = get_url('DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS', 'https://selling-online-overseas.export.great.gov.uk')  # noqa
SINGLE_SIGN_ON = get_url('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', HOME / 'sso')
EXPORT_OPPORTUNITIES = get_url('DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES', HOME / 'export-opportunities')
FIND_A_BUYER = get_url('DIRECTORY_CONSTANTS_URL_FIND_A_BUYER', HOME / 'find-a-buyer')
SINGLE_SIGN_ON_PROFILE = get_url('DIRECTORY_CONSTANTS_URL_SSO_PROFILE', HOME / 'profile')

# Export readiness/great domestic article sections
ADVICE = HOME / 'advice'
ADVICE_CREATE_AN_EXPORT_PLAN = ADVICE / 'create-an-export-plan'
ADVICE_FIND_AN_EXPORT_MARKET = ADVICE / 'find-an-export-market'
ADVICE_DEFINE_ROUTE_TO_MARKET = ADVICE / 'define-route-to-market'
ADVICE_GET_EXPORT_FINANCE_AND_FUNDING = ADVICE / 'get-export-finance-and-funding'
ADVICE_MANAGE_PAYMENT_FOR_EXPORT_ORDERS = ADVICE / 'manage-payment-for-export-orders'
ADVICE_PREPARE_TO_DO_BUSINESS_IN_A_FOREIGN_COUNTRY = ADVICE / 'prepare-to-do-business-in-a-foreign-country'
ADVICE_MANAGE_LEGAL_AND_ETHICAL_COMPLIANCE = ADVICE / 'manage-legal-and-ethical-compliance'
ADVICE_PREPARE_FOR_EXPORT_PROCEDURES_AND_LOGISTICS = ADVICE / 'prepare-for-export-procedures-and-logistics'

SEARCH = HOME / 'search'
MARKETS = HOME / 'markets'
GET_FINANCE = HOME / 'get-finance'
GREAT_DOMESTIC_NEWS = HOME / 'news'
SERVICES = HOME / 'services'
TERMS_AND_CONDITIONS = HOME / 'terms-and-conditions'
ABOUT = HOME / 'about'
PRIVACY_AND_COOKIES = HOME / 'privacy-and-cookies'
ACCESSIBILITY = HOME / 'accessibility-statement'
COOKIE_PREFERENCE_SETTINGS = HOME / 'cookies'
PERFORMANCE_DASHBOARD = HOME / 'performance-dashboard'
CONTACT_US = HOME / 'contact'
FEEDBACK = CONTACT_US / 'feedback'
OFFICE_FINDER = CONTACT_US / 'office-finder'

DIT = 'https://www.gov.uk/government/organisations/department-for-international-trade'

INTERNATIONAL_CONTACT_TRIAGE = CONTACT_US / 'triage/international'

# Legacy great/export readiness article/persona/triage urls
CUSTOM_PAGE = HOME / 'custom'
EXPORTING_NEW = HOME / 'new'
EXPORTING_OCCASIONAL = HOME / 'occasional'
EXPORTING_REGULAR = HOME / 'regular'
GUIDANCE_MARKET_RESEARCH = HOME / 'market-research'
GUIDANCE_CUSTOMER_INSIGHT = HOME / 'customer-insight'
GUIDANCE_FINANCE = HOME / 'finance'
GUIDANCE_BUSINESS_PLANNING = HOME / 'business-planning'
GUIDANCE_GETTING_PAID = HOME / 'getting-paid'
GUIDANCE_OPERATIONS_AND_COMPLIANCE = HOME / 'operations-and-compliance'
