import csv
import json
from operator import itemgetter
from pathlib import Path

from directory_constants import cms, company_types, expertise, helpers, sectors, user_roles, exporting, export_plan


INDUSTRIES = (
    (sectors.AEROSPACE, 'Aerospace'),
    (sectors.ADVANCED_MANUFACTURING, 'Advanced manufacturing'),
    (sectors.AIRPORTS, 'Airports'),
    (
        sectors.AGRICULTURE_HORTICULTURE_AND_FISHERIES,
        'Agriculture, horticulture and fisheries'
    ),
    (sectors.AUTOMOTIVE, 'Automotive'),
    (
        sectors.BIOTECHNOLOGY_AND_PHARMACEUTICALS,
        'Biotechnology and pharmaceuticals'
    ),
    (
        sectors.BUSINESS_AND_CONSUMER_SERVICES,
        'Business and consumer services'
    ),
    (sectors.CHEMICALS, 'Chemicals'),
    (
        sectors.CLOTHING_FOOTWEAR_AND_FASHION,
        'Clothing, footwear and fashion'),
    (sectors.COMMUNICATIONS, 'Communications'),
    (sectors.CONSTRUCTION, 'Construction'),
    (sectors.CREATIVE_AND_MEDIA, 'Creative and media'),
    (sectors.EDUCATION_AND_TRAINING, 'Education and training'),
    (sectors.ELECTRONICS_AND_IT_HARDWARE, 'Electronics and IT hardware'),
    (sectors.ENVIRONMENT, 'Environment'),
    (
        sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'Financial and professional services'
    ),
    (sectors.FOOD_AND_DRINK, 'Food and drink'),
    (
        sectors.GIFTWARE_JEWELLERY_AND_TABLEWARE,
        'Giftware, jewellery and tableware'
    ),
    (sectors.GLOBAL_SPORTS_INFRASTRUCTURE, 'Global sports infrastructure'),
    (sectors.HEALTHCARE_AND_MEDICAL, 'Healthcare and medical'),
    (
        sectors.HOUSEHOLD_GOODS_FURNITURE_AND_FURNISHINGS,
        'Household goods, furniture and furnishings'
    ),
    (sectors.LIFE_SCIENCES, 'Life sciences'),
    (sectors.LEISURE_AND_TOURISM, 'Leisure and tourism'),
    (sectors.LEGAL_SERVICES, 'Legal services'),
    (sectors.MARINE, 'Marine'),
    (
        sectors.MECHANICAL_ELECTRICAL_AND_PROCESS_ENGINEERING,
        'Mechanical electrical and process engineering'
    ),
    (sectors.METALLURGICAL_PROCESS_PLANT, 'Metallurgical process plant'),
    (
        sectors.METALS_MINERALS_AND_MATERIALS,
        'Metals, minerals and materials'
    ),
    (sectors.MINING, 'Mining'),
    (sectors.OIL_AND_GAS, 'Oil and gas'),
    (sectors.PORTS_AND_LOGISTICS, 'Ports and logistics'),
    (sectors.POWER, 'Power'),
    (sectors.RAILWAYS, 'Railways'),
    (sectors.RENEWABLE_ENERGY, 'Renewable energy'),
    (sectors.RETAIL_AND_LUXURY, 'Retail and luxury'),
    (sectors.SECURITY, 'Security'),
    (
        sectors.SOFTWARE_AND_COMPUTER_SERVICES,
        'Software and computer services'
    ),
    (
        sectors.TEXTILES_INTERIOR_TEXTILES_AND_CARPETS,
        'Textiles, interior textiles and carpets'
    ),
    (sectors.WATER, 'Water'),
)

EMPLOYEES = (
    ('1-10', '1-10'),
    ('11-50', '11-50'),
    ('51-200', '51-200'),
    ('201-500', '201-500'),
    ('501-1000', '501-1,000'),
    ('1001-10000', '1,001-10,000'),
    ('10001+', '10,001+'),
)

CMS_APP_CHOICES = [
    (cms.FIND_A_SUPPLIER, 'Find a Supplier'),
    (cms.EXPORT_READINESS, 'Export Readiness'),
    (cms.INVEST, 'Invest'),
    (cms.COMPONENTS, 'Components'),
    (cms.GREAT_INTERNATIONAL, 'Great International')
]


CONTACT_OPTIONS = (
    ('EMAIL', 'Email'),
    ('PHONE', 'Phone'),
)

EXPERTISE_LANGUAGES = [
    ('ab', 'Abkhazian'),
    ('aa', 'Afar'),
    ('af', 'Afrikaans'),
    ('ak', 'Akan'),
    ('sq', 'Albanian'),
    ('am', 'Amharic'),
    ('ar', 'Arabic'),
    ('an', 'Aragonese'),
    ('hy', 'Armenian'),
    ('as', 'Assamese'),
    ('av', 'Avaric'),
    ('ay', 'Aymara'),
    ('az', 'Azerbaijani'),
    ('bm', 'Bambara'),
    ('ba', 'Bashkir'),
    ('eu', 'Basque'),
    ('be', 'Belarusian'),
    ('bn', 'Bengali'),
    ('bi', 'Bislama'),
    ('bs', 'Bosnian'),
    ('br', 'Breton'),
    ('bg', 'Bulgarian'),
    ('my', 'Burmese'),
    ('yue', 'Cantonese'),
    ('ca', 'Catalan'),
    ('km', 'Central Khmer'),
    ('ce', 'Chechen'),
    ('zh', 'Chinese (written, simplified)'),
    ('kw', 'Cornish'),
    ('co', 'Corsican'),
    ('cr', 'Cree'),
    ('hr', 'Croatian'),
    ('cs', 'Czech'),
    ('da', 'Danish'),
    ('dv', 'Divehi; Dhivehi; Maldivian'),
    ('nl', 'Dutch; Flemish'),
    ('dz', 'Dzongkha'),
    ('en', 'English'),
    ('et', 'Estonian'),
    ('ee', 'Ewe'),
    ('fo', 'Faroese'),
    ('fj', 'Fijian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('ff', 'Fulah'),
    ('gd', 'Gaelic'),
    ('gl', 'Galician'),
    ('lg', 'Ganda'),
    ('ka', 'Georgian'),
    ('de', 'German'),
    ('el', 'Greek'),
    ('gn', 'Guarani'),
    ('gu', 'Gujarati'),
    ('ht', 'Haitian; Haitian Creole'),
    ('ha', 'Hausa'),
    ('he', 'Hebrew'),
    ('hz', 'Herero'),
    ('hi', 'Hindi'),
    ('ho', 'Hiri Motu'),
    ('hu', 'Hungarian'),
    ('is', 'Icelandic'),
    ('ig', 'Igbo'),
    ('id', 'Indonesian'),
    ('ik', 'Inupiaq'),
    ('ga', 'Irish'),
    ('it', 'Italian'),
    ('ja', 'Japanese'),
    ('jv', 'Javanese'),
    ('kn', 'Kannada'),
    ('kr', 'Kanuri'),
    ('ks', 'Kashmiri'),
    ('kk', 'Kazakh'),
    ('ki', 'Kikuyu; Gikuyu'),
    ('rw', 'Kinyarwanda'),
    ('ky', 'Kirghiz; Kyrgyz'),
    ('kv', 'Komi'),
    ('kg', 'Kongo'),
    ('ko', 'Korean'),
    ('kj', 'Kuanyama; Kwanyama'),
    ('ku', 'Kurdish'),
    ('lo', 'Lao'),
    ('lv', 'Latvian'),
    ('li', 'Limburgan; Limburger; Limburgish'),
    ('ln', 'Lingala'),
    ('lt', 'Lithuanian'),
    ('lu', 'Luba-Katanga'),
    ('lb', 'Luxembourgish; Letzeburgesch'),
    ('mk', 'Macedonian'),
    ('mg', 'Malagasy'),
    ('ms', 'Malay'),
    ('ml', 'Malayalam'),
    ('mt', 'Maltese'),
    ('gv', 'Manx'),
    ('cmn', 'Mandarin'),
    ('mi', 'Maori'),
    ('mr', 'Marathi'),
    ('mh', 'Marshallese'),
    ('mn', 'Mongolian'),
    ('na', 'Nauru'),
    ('ng', 'Ndonga'),
    ('ne', 'Nepali'),
    ('se', 'Northern Sami'),
    ('no', 'Norwegian'),
    ('oj', 'Ojibwa'),
    ('or', 'Oriya'),
    ('om', 'Oromo'),
    ('os', 'Ossetian; Ossetic'),
    ('pa', 'Panjabi; Punjabi'),
    ('fa', 'Persian'),
    ('pl', 'Polish'),
    ('pt', 'Portuguese'),
    ('ps', 'Pushto; Pashto'),
    ('qu', 'Quechua'),
    ('ro', 'Romanian; Moldavian; Moldovan'),
    ('rm', 'Romansh'),
    ('rn', 'Rundi'),
    ('ru', 'Russian'),
    ('sm', 'Samoan'),
    ('sg', 'Sango'),
    ('sc', 'Sardinian'),
    ('sr', 'Serbian'),
    ('sn', 'Shona'),
    ('ii', 'Sichuan Yi; Nuosu'),
    ('sd', 'Sindhi'),
    ('si', 'Sinhala; Sinhalese'),
    ('sk', 'Slovak'),
    ('sl', 'Slovenian'),
    ('so', 'Somali'),
    ('st', 'Sotho, Southern'),
    ('es', 'Spanish'),
    ('su', 'Sundanese'),
    ('sw', 'Swahili'),
    ('ss', 'Swati'),
    ('sv', 'Swedish'),
    ('ty', 'Tahitian'),
    ('tg', 'Tajik'),
    ('ta', 'Tamil'),
    ('tt', 'Tatar'),
    ('te', 'Telugu'),
    ('th', 'Thai'),
    ('bo', 'Tibetan'),
    ('ti', 'Tigrinya'),
    ('to', 'Tonga (Tonga Islands)'),
    ('ts', 'Tsonga'),
    ('tn', 'Tswana'),
    ('tr', 'Turkish'),
    ('tk', 'Turkmen'),
    ('tw', 'Twi'),
    ('ug', 'Uighur; Uyghur'),
    ('uk', 'Ukrainian'),
    ('ur', 'Urdu'),
    ('uz', 'Uzbek'),
    ('ve', 'Venda'),
    ('vi', 'Vietnamese'),
    ('wa', 'Walloon'),
    ('cy', 'Welsh'),
    ('yi', 'Yiddish'),
    ('yo', 'Yoruba'),
    ('za', 'Zhuang; Chuang'),
    ('zu', 'Zulu'),
]


EU_COUNTRIES = {
    'AT': 'Austria',
    'BE': 'Belgium',
    'BG': 'Bulgaria',
    'HR': 'Croatia',
    'CY': 'Cyprus',
    'CZ': 'Czechia',
    'DK': 'Denmark',
    'EE': 'Estonia',
    'FI': 'Finland',
    'FR': 'France',
    'DE': 'Germany',
    'GR': 'Greece',
    'HU': 'Hungary',
    'IE': 'Ireland',
    'IT': 'Italy',
    'LV': 'Latvia',
    'LT': 'Lithuania',
    'LU': 'Luxembourg',
    'MT': 'Malta',
    'NL': 'Netherlands',
    'PL': 'Poland',
    'PT': 'Portugal',
    'RO': 'Romania',
    'SK': 'Slovakia',
    'SI': 'Slovenia',
    'ES': 'Spain',
    'SE': 'Sweden'
}

EXPERTISE_REGION_CHOICES = [
    ('NORTH_EAST', 'North East'),
    ('NORTH_WEST', 'North West'),
    ('NORTHERN_IRELAND', 'Northern Ireland'),
    ('YORKSHIRE_AND_HUMBER', 'Yorkshire and the Humber'),
    ('EAST_MIDLANDS', 'East Midlands'),
    ('WEST_MIDLANDS', 'West Midlands'),
    ('EASTERN', 'East of England'),
    ('LONDON', 'London'),
    ('SOUTH_EAST', 'South East'),
    ('SOUTH_WEST', 'South West'),
    ('SCOTLAND', 'Scotland'),
    ('WALES', 'Wales'),
]

EXPERTISE_FINANCIAL = [(i, i) for i in expertise.FINANCIAL]

EXPERTISE_MANAGEMENT_CONSULTING = [
    (i, i) for i in expertise.MANAGEMENT_CONSULTING
]

EXPERTISE_HUMAN_RESOURCES = [(i, i) for i in expertise.HUMAN_RESOURCES]

EXPERTISE_LEGAL = [(i, i) for i in expertise.LEGAL]

EXPERTISE_PUBLICITY = [(i, i) for i in expertise.PUBLICITY]

EXPERTISE_BUSINESS_SUPPORT = [(i, i) for i in expertise.BUSINESS_SUPPORT]

LEAD_GENERATION_EXPORT_DESTINATIONS = (
    ('CN', 'China'),
    ('DE', 'Germany'),
    ('IN', 'India'),
    ('JP', 'Japan'),
    ('US', 'United States'),
)


COMPANY_TYPES = (
    (
        company_types.COMPANIES_HOUSE,
        'A business registered with Companies House'
    ),
    (company_types.CHARITY, 'Charity'),
    (company_types.PARTNERSHIP, 'Partnership'),
    (company_types.SOLE_TRADER, 'Sole Trader'),
    ('OTHER', 'Other UK business not registered in Companies House'),
)

USER_ROLES = (
    (user_roles.ADMIN, 'Admin'),
    (user_roles.EDITOR, 'Editor'),
    (user_roles.MEMBER, 'Member'),
)

fixtures = Path(__file__).parent / 'fixtures'


# from https://www.registers.service.gov.uk/registers/country
with (fixtures / 'country.json').open('r') as f:
    COUNTRY_CHOICES = []
    for country in json.loads(f.read()).values():
        for item in country['item']:
            if 'end-date' not in item:
                COUNTRY_CHOICES.append((item['country'], item['name']))
    COUNTRY_CHOICES.sort(key=itemgetter(1))

# from https://www.gov.uk/government/publications/
# standard-industrial-classification-of-economic-activities-sic

with (fixtures / 'sic.csv').open('r') as f:
    reader = csv.DictReader(f)
    SIC_CODES = [(row['SIC Code'], row['Description']) for row in reader]
    SIC_CODES.sort(key=itemgetter(1))


# from https://data.trade.gov.uk/catalogue/reference-data-sets/reference/dit-sector-list
# old list which can't change for now since it's used in BAU domestic / directory-cms for tagging sectors
with (fixtures / 'dit-sector-list-legacy.json').open('r') as f:
    SECTORS = []
    for sector in json.loads(f.read()):
        SECTORS.append((sector['Sector code'], sector['Sector name']))
    SECTORS.sort(key=itemgetter(1))


# from https://data.trade.gov.uk/catalogue/reference-data-sets/reference/dit-sector-list
# Use for latest sector list for newer files
with (fixtures / 'dit-sector-list.json').open('r') as f:
    # Create a list of unique Sector names, we order by the ID as we want the first one in the list to get top level
    SECTOR_NAMES = []
    all_sectors = json.loads(f.read())
    all_sectors.sort(key=itemgetter('Sector ID'))
    seen = set()
    for sector in all_sectors:
        if sector['Sector name'] not in seen:
            SECTOR_NAMES.append((sector['Sector ID'], sector['Sector name']))
            seen.add(sector['Sector name'])
    SECTOR_NAMES.sort(key=itemgetter(1))


COUNTRIES_AND_TERRITORIES = helpers.build_country_choices()
COUNTRIES_AND_TERRITORIES_REGION = helpers.build_country_region_choices()


PRODUCT_PROMOTIONAL_CHOICES = (
    (exporting.MARKETING_AT_EVENTS, 'Marketing at events'),
    (exporting.ONLINE_MARKETING, 'Online marketing'),
    (exporting.OTHER, 'Other'),
)


MARKET_ROUTE_CHOICES = (
    (exporting.DIRECT_SALES, 'Direct sales'),
    (exporting.INTERNATIONAL_E_COMMERCE, 'International e-commerce'),
    (exporting.AGENT_OR_DISTRIBUTOR, 'Agent or distributor'),
    (exporting.LICENSING, 'Licensing'),
    (exporting.FRANCHISING, 'Franchising'),
    (exporting.JOINT_VENTURES, 'Joint ventures'),
    (exporting.SET_UP_A_BUSINESS_ABROAD, 'Set up a business abroad'),
    (exporting.OTHER, 'Other'),
)

TURNOVER_CHOICES = (
    ('<83k', 'Below £83,000 (Below VAT registered)'),
    ('83k-499.999k', '£83,000 up to £499,999'),
    ('50k-1999.999k', '£500,000 up to £1,999,999'),
    ('2m-4999.999k', '£2 million up to £4,999,999'),
    ('5m-9999.999k', '£5 million up to £9,999,999'),
    ('10m-49999.999k', '£10 million up to £49,999,999'),
    ('50m+', '£50 million or over'),
    ('', 'Don\'t know')
)

TARGET_AGE_GROUP_CHOICES = (
    ('0-14', '0-14 year olds'),
    ('15-19', '15-19 year olds'),
    ('20-24', '20-24 year olds'),
    ('25-34', '25-34 year olds'),
    ('35-44', '35-44 year olds'),
    ('45-54', '45-54 year olds'),
    ('55-64', '55-64 year olds'),
    ('65+', '65 years old and over'),
)

EXPORT_UNITS = (
    ('m', 'metre(s)'),
    ('g', 'gram(s)'),
    ('kg', 'kilogram(s)'),
    ('piece', 'piece(s)'),
    ('set', 'set(s)'),
    ('pack', 'pack(s)'),
)

EXPORT_TIMEFRAME = (
    ('d', 'day(s)'), ('m', 'month(s)'), ('y', 'year(s)')
)

FUNDING_OPTIONS = (
    (export_plan.BANK_LOAN, 'Bank loan'), (export_plan.GOVERNMENT, 'Finance support from government'),
    (export_plan.FINANCE_PLATFORMS, 'Finance platforms'), (export_plan.PEER_TO_PEER_LOANS, 'Peer-to-peer loan'),
    (export_plan.EQUITY_FINANCE, 'Equity finance'), (export_plan.OTHER, 'Other'),
)

TRANSPORT_OPTIONS = (
    (export_plan.EX_WORKS, 'Ex Works (EXW)'), (export_plan.FREE_CARRIER, 'Free Carrier (FCA)'),
    (export_plan.CARRIER_INSURANCE_PAID, 'Carrier and Insurance Paid to (CIP)'),
    (export_plan.DELIVERED_PLACE_UNLOADED, 'Delivered at Place Unloaded (DPU)'),
    (export_plan.DELIVERED_AT_PLACE, 'Delivered at Place (DAP)'),
    (export_plan.DELIVERED_DUTY_PAID, 'Delivered Duty Paid (DDP)'),
)

WATER_TRANSPORT_OPTIONS = (
    (export_plan.FREE_ALONG_SHIP, 'Free Alongside Ship (FAS)'), (export_plan.FREE_ON_BOARD, 'Free on Board (FOB)'),
    (export_plan.COST_AND_FREIGHT, 'Cost and Freight (CFR)'),
    (export_plan.COST_INSURANCE_FREIGHT, 'Cost, Insurance and Freight (CIF)')
)

PAYMENT_METHOD_OPTIONS = (
    (export_plan.INTERNATIONAL_BANK_TRANSFER, 'International bank transfers'),
    (export_plan.CREDIT_DEBIT, 'Credit or debit card payments'),
    (export_plan.MERCHANT_SERVICES, 'Merchant services'),
    (export_plan.LOCAL_BANK_TRANSFERS, 'Local bank transfers'), ('other', 'Other')
)

PAYMENT_TERM_OPTIONS = (
    (export_plan.PAYMENT_IN_ADVANCE, 'Payment in advance'),
    (export_plan.LETTER_OF_CREDIT, 'Letter of credit'),
    (export_plan.BANK_DOCUMENTARY_COLLECTION, 'Bank collection or documentary collections (D/C)'),
    (export_plan.OPEN_ACCOUNT, 'Open account'), (export_plan.OTHER, 'Other')
)

RISK_LIKELIHOOD_OPTIONS = (
    (export_plan.RARE, 'Rare'),
    (export_plan.UNLIKELY, 'Unlikely'),
    (export_plan.POSSIBLE, 'Possible'),
    (export_plan.LIKELY, 'Likely'),
    (export_plan.CERTAIN, 'Certain'),
)

RISK_IMPACT_OPTIONS = (
    (export_plan.TRIVIAL, 'Trivial'),
    (export_plan.MINOR, 'Minor'),
    (export_plan.MODERATE, 'Moderate'),
    (export_plan.MAJOR, 'Major'),
    (export_plan.SEVERE, 'Severe'),
)
