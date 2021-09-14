from upswingutil.resource import access_secret_version
import holidayapi
import requests
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


def get_holiday_list_v2(countryCode: str, year: int, month: int, date: int):
    project = os.getenv('G_CLOUD_PROJECT', 'aura-staging-31cae')
    apiKey = access_secret_version(project, 'abstractHolidayAPI', '1')
    response = requests.get(f"https://holidays.abstractapi.com/v1/?api_key={apiKey}&country={countryCode}&year={year}&month={month}")
    result = response.json()
    return [item for item in result if int(item['date_month']) >= month]
