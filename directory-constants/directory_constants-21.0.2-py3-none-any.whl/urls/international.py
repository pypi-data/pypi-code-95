from directory_constants.helpers import UrlString, get_url
from directory_constants.urls.domestic import INTERNATIONAL_CONTACT_TRIAGE

HOME = UrlString(get_url('DIRECTORY_CONSTANTS_URL_INTERNATIONAL', 'https://great.gov.uk/international/'))
CONTENT_ROOT = HOME / 'content'

# about the UK
ABOUT_UK_HOME = CONTENT_ROOT / 'about-uk'
ABOUT_UK_WHY_CHOOSE_UK = ABOUT_UK_HOME / 'why-choose-uk'
ABOUT_UK_INDUSTRIES = CONTENT_ROOT / 'industries'
ABOUT_UK_REGIONS = ABOUT_UK_HOME / 'regions'
ABOUT_UK_CONTACT = INTERNATIONAL_CONTACT_TRIAGE

# expand
expand_slug = get_url('DIRECTORY_CONSTANTS_EXPAND_SLUG', 'invest')  # for the transition from invest/ to expand/
EXPAND_HOME = HOME / expand_slug
EXPAND_CONTENT_ROOT = CONTENT_ROOT / expand_slug
EXPAND_HOW_TO_SETUP = CONTENT_ROOT / 'how-to-setup-in-the-uk'
EXPAND_HOW_TO_SETUP_VISAS_AND_MIGRATION = EXPAND_HOW_TO_SETUP / 'uk-visas-and-migration'
EXPAND_HOW_TO_SETUP_TAX_AND_INCENTIVES = EXPAND_HOW_TO_SETUP / 'uk-tax-and-incentives'
EXPAND_HOW_TO_DO_BUSINESS = CONTENT_ROOT / 'how-to-do-business-with-the-uk'
EXPAND_HOW_WE_HELP = EXPAND_CONTENT_ROOT / 'how-we-help-you-expand'
EXPAND_CONTACT = EXPAND_HOME / 'contact'

# capital invest
CAPITAL_INVEST_HOME = CONTENT_ROOT / 'capital-invest'
CAPITAL_INVEST_OPPORTUNITIES = CONTENT_ROOT / 'opportunities'
CAPITAL_INVEST_HOW_WE_HELP = CAPITAL_INVEST_HOME / 'how-we-help-you-invest-capital'
CAPITAL_INVEST_CONTACT = CAPITAL_INVEST_HOME / 'contact'

# trade
TRADE_HOME = HOME / 'trade'
TRADE_FAS = TRADE_HOME
TRADE_FAS_SEARCH = TRADE_FAS / 'search'
TRADE_CONTENT_ROOT = CONTENT_ROOT / 'trade'
TRADE_HOW_WE_HELP = TRADE_CONTENT_ROOT / 'how-we-help-you-buy'
TRADE_CONTACT = TRADE_HOME / 'contact'

# about dit
ABOUT_DIT_HOME = CONTENT_ROOT / 'about-us'
ABOUT_DIT_CONTACT = INTERNATIONAL_CONTACT_TRIAGE

# news
NEWS = CONTENT_ROOT / 'news/'

# contact
CONTACT = INTERNATIONAL_CONTACT_TRIAGE
CONTACT_US = HOME / 'contact/'

# isd
EXPAND_ISD_HOME = HOME / 'investment-support-directory'
EXPAND_ISD_SEARCH = EXPAND_ISD_HOME / 'search'
CAPITAL_INVEST_ISD = HOME / 'capital-invest' / 'investment-support-directory'
CAPITAL_INVEST_ISD_SEARCH = CAPITAL_INVEST_ISD / 'search'
