from upswingutil.resource import access_secret_version
import holidayapi
import os

KEY_NAME = 'holidayAPIkey'


def get_holiday_list(countryCode: str, year: int, month: int, date: int):
    project = os.getenv('G_CLOUD_PROJECT', 'aura-staging-31cae')
    apiKey = access_secret_version(project, KEY_NAME, '1')
    hapi = holidayapi.v1(apiKey)
    parameters = {
        # Required
        'country': countryCode,
        'year': year,
        # Optional
        'language': 'en',
        'month': month,
        'day': date,
        # 'previous': True,
        'upcoming': True,
        # 'public':   True,
        # 'pretty':   True,
    }
    holidays = hapi.holidays(parameters)
    return holidays
