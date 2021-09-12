import re
from cnvrg.modules.errors import UserError
class CnvrgBase():
    @staticmethod
    def get_owner_and_project_from_url(url):
        return CnvrgBase.parse_url(url, 'projects')

    @staticmethod
    def get_owner_and_dataset_from_url(url):
        return CnvrgBase.parse_url(url, 'datasets')

    @staticmethod
    def get_owner_and_library_from_url(url):
        return CnvrgBase.parse_url(url, 'libraries')

    @staticmethod
    def parse_url(url, search_for):
        reg = re.search(re.compile("([A-Za-z0-9-_]+)/{search_for}/([A-Za-z0-9-_]+)".format(search_for=search_for)), url)
        if not reg:
            raise UserError("Cant parse the given url")
        return reg.groups()