from upswingutil.resource import access_secret_version
import os


KEY_NAME = 'holidayAPIkey'


def get_holiday_list():
    project = os.getenv('G_CLOUD_PROJECT', 'aura-staging-31cae')
    print(project)
    apiKey = access_secret_version(project, KEY_NAME, '1')
    print(apiKey)
