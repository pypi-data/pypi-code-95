import json

from abc import abstractmethod

import nacos


class Config(dict):
    """Base class for regia config. All config must inherit from this class"""

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            pass

    @abstractmethod
    def initialize(self) -> dict:
        """
        配置抽象接口,所有实现类在此完成数据的读取并返回
        :return:
        """
        ...

    def render(self, **kwargs):
        data = self.initialize()
        kwargs.update(data)
        self.update(kwargs)


class JsonConfig(Config):
    """json config implement Config"""

    def __init__(self, path):
        super(JsonConfig, self).__init__()
        self.path = path

    def initialize(self) -> dict:
        with open(self.path, 'r') as f:
            return json.loads(f.read())


class NaconsConfig(Config):
    """Nacons config implement Config"""

    def __init__(self, data_id: str, group: str, **kwargs):
        super(NaconsConfig, self).__init__()
        self.server_address = kwargs.pop('server_address', 'localhost')
        self.data_id = data_id
        self.group = group
        self.kwargs = kwargs

    def initialize(self) -> dict:
        client = nacos.NacosClient(server_addresses=self.server_address, **self.kwargs)
        content = client.get_config(self.data_id, self.group)
        return json.loads(content)
