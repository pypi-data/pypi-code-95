import typing

from wisdoms_dapr import exceptions, shares


class APPConfig(object):
    """APP Config"""

    def __init__(self, config: dict, *, default_config: typing.Optional[dict] = None):
        self._config = config
        self._default_config = default_config

    def _get_app_config_item(self, item: typing.Hashable):
        """Get APP Config Item"""

        try:
            return self._config[item]
        except KeyError:
            if not isinstance(self._default_config, dict):
                raise exceptions.ServiceConfigException(f"app config({self._config}) item `{item}` is not exist")

            try:
                return self._default_config[item]
            except KeyError:
                raise exceptions.ServiceConfigException(f"app config({self._config}) item `{item}` is not exist")

    def __call__(self, item: typing.Hashable):
        return self._get_app_config_item(item)

    def __getitem__(self, item: typing.Hashable):
        return self._get_app_config_item(item)

    def __getattr__(self, item: typing.Hashable):
        return self._get_app_config_item(item)


class APPsConfig(object):
    """
    APPs Config
    """

    def __init__(
        self,
        config: dict,
        config_item: str,
        *,
        default_appid: typing.Optional[str] = shares.DEFAULT_APPID,
        lookup_default: bool = True
    ):
        """
        Init Apps Config
        :param config: all service config
        :param config_item: service apps config item, such as: service
        :param default_appid: appid use default appid config when appid config miss and default appid is exist.
        :param lookup_default: whether lookup default config item when appid config item is not exist.
        """

        try:
            apps_config = config[config_item]
            if not isinstance(apps_config, dict):
                raise exceptions.ServiceConfigException(
                    msg=f"`{config_item}` apps config value({apps_config}) type({type(apps_config)}) is not dict type"
                )

            self._config = config
            self._config_item = config_item
            self._default_appid = default_appid
            self._lookup_default = lookup_default
            self.apps_config = apps_config
        except Exception as e:
            raise exceptions.ServiceConfigException(msg=str(e))

    def _get_app_config(self, appid: typing.Optional[str] = None) -> APPConfig:
        """Get app config"""

        if not appid or self.apps_config.get(appid) is None:
            if self._default_appid and self.apps_config.get(self._default_appid):
                v = self.apps_config[self._default_appid]
            else:
                raise exceptions.ServiceConfigException(msg=f"get config item `{appid}` failed")
        else:
            v = self.apps_config[appid]

        if not isinstance(v, dict):
            raise exceptions.ServiceConfigException(
                msg=f"`{appid}` config item value({v}) type({type(v)}) is not dict type"
            )

        if self._lookup_default and self._get_default_app_config():
            return APPConfig(config=v, default_config=self._get_default_app_config())

        return APPConfig(config=v)

    def _get_default_app_config(self) -> typing.Optional[dict]:
        """Get default app config"""

        if self._default_appid:
            return self.apps_config.get(self._default_appid)

        return None

    def __call__(self, appid: typing.Optional[str] = None) -> APPConfig:
        return self._get_app_config(appid)

    def __getitem__(self, appid: typing.Optional[str] = None) -> APPConfig:
        return self._get_app_config(appid)

    def __getattr__(self, appid: typing.Optional[str] = None) -> APPConfig:
        return getattr(self, '_get_app_config')(appid)
