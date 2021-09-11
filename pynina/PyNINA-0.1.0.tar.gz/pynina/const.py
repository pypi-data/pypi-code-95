ENDPOINT_REGIONAL_CODE: str = "https://www.xrepository.de/api/xrepository/urn:de:bund:destatis:bevoelkerungsstatistik:schluessel:rs_2021-07-31/download/Regionalschl_ssel_2021-07-31.json"
ENDPOINT_NINA_BASE: str = "https://warnung.bund.de/api31/dashboard/"


class ReadOnlyClass(type):
    def __setattr__(self, name, value):
        raise ValueError(name)
