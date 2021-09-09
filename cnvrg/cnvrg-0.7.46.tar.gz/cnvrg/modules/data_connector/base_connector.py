import cnvrg.helpers.apis_helper as apis_helper
import cnvrg.helpers.param_build_helper as param_build_helper
import cnvrg.modules.errors as errors
class BaseConnector():
    def __init__(self, data_connector, info=None):
        org, data_connector = param_build_helper.parse_params(data_connector, param_build_helper.DATA_CONNECTOR)
        self._org = org
        self._data_connector = data_connector
        self.info = None
        self.__init_data_connector(info=info)

    @staticmethod
    def key_type():
        raise errors.CnvrgError("Not implemented")

    def connector_type(self):
        return self.info.get("connector_type") or 'dataset'

    def __init_data_connector(self, info=None):
        self.info = info or apis_helper.get(self.__base_url()).get("data_connector")
        self.data = self.info.get("credentials")

    def __base_url(self):
        return apis_helper.url_join('users', self._org, "data_connectors", self._data_connector)

    @classmethod
    def create(cls, title, **kwargs):
        data_connector = {"title": title, "credentials": kwargs, "connector_type": cls.key_type()}
        resp = apis_helper.post(apis_helper.url_join("users", apis_helper.credentials.owner, 'data_connectors'), data={"data_connector": data_connector})
        payload = resp.get("data_connector")
        if not payload: raise errors.CnvrgError("Cant create data connector")
        return cls(payload.get("slug"))