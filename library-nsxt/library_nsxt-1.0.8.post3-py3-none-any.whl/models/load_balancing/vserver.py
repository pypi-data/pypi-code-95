from library_nsxt.models import NSXTModel

_ENABLED_KEY = "enabled"
_IP_ADDRESS_KEY = "ip_address"
_PORTS_KEY = "ports"
_POOL_KEY = "pool_path"
_POOL_ID_KEY = "pool_id"
_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_TAGS_KEY = "tags"

_TAG_TENANT_SCOPE = "tenant"


class VServer(NSXTModel):
    """Model for the NSX-T Virtual Server object"""

    def __init__(self, id, display_name, ip_address, ports, tags=None, enabled=True):
        """
        Generates a new Load balancer Virtual server

        :param str id: The internal id of the virtual server.
        :param str display_name: The name displayed to the user.
        :param str ip_address: The ip address of the virtual server.
        :param list[str] ports: The list of single ports or port ranges that this virtual server will balance through.
        :param set[str] tags: The tenant tags associated to the virtual server.
        :param bool enabled: If True, the virtual server is enabled.
        """
        NSXTModel.__init__(self, id, display_name, revision=None)
        self.ip_address = ip_address
        self.ports = ports
        self.tags = tags if tags is not None else {}
        self.enabled = enabled

    def is_declarative(self):
        raise NotImplementedError("VServer model must implement a get_pool_path method.")

    def to_json(self):
        raise TypeError("Virtual servers should not be saved to device.")

    def get_pool_path(self):
        raise NotImplementedError("VServer model must implement a get_pool_path method.")

    def get_pool_update_path(self):
        raise NotImplementedError("VServer model must implement a get_pool_update_path method.")

    @classmethod
    def from_json(cls, raw_json):
        NSXTModel.from_json(raw_json)

    @classmethod
    def _parse_tags(cls, raw_tags):
        return {tag for scope, tag in NSXTModel._parse_tags(raw_tags) if scope == _TAG_TENANT_SCOPE}


class VServerImperative(VServer):
    """Implementation of VServer through the imperative API."""

    __BASE_POOL_PATH = "/loadbalancer/pools/%s"
    __UPDATE_MEMBER_PARAM = "?action=UPDATE_MEMBERS"

    def __init__(self, id, display_name, ip_address, ports, pool_id, tags=None, enabled=True):
        """
        Generates a new Load balancer imperative Virtual server.

        :param str id: The internal id of the virtual server.
        :param str display_name: The name displayed to the user.
        :param str ip_address: The ip address of the virtual server.
        :param list[str] ports: The list of single ports or port ranges that this virtual server will balance through.
        :param str pool_id: Id of the Load balancer pool associated with this virtual server.
        :param set[str] tags: The tenant tags associated to the virtual server.
        :param bool enabled: If True, the virtual server is enabled.
        """
        VServer.__init__(self, id, display_name, ip_address, ports, tags=tags, enabled=enabled)
        self.pool_id = pool_id

    def is_declarative(self):
        return False

    def get_pool_path(self):
        return self.__BASE_POOL_PATH % self.pool_id

    def get_pool_update_path(self):
        return self.get_pool_path() + self.__UPDATE_MEMBER_PARAM

    @classmethod
    def from_json(cls, raw_json):
        return VServerImperative(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            ip_address=raw_json[_IP_ADDRESS_KEY],
            ports=raw_json[_PORTS_KEY],
            tags=cls._parse_tags(raw_json[_TAGS_KEY]) if _TAGS_KEY in raw_json else set(),
            enabled=raw_json[_ENABLED_KEY],
            pool_id=raw_json[_POOL_ID_KEY],
        )


class VServerDeclarative(VServer):
    """Implementation of VServer through the declarative API."""

    def __init__(self, id, display_name, ip_address, ports, pool_path, tags=None, enabled=True):
        """
        Generates a new Load balancer imperative Virtual server.

        :param str id: The internal id of the virtual server.
        :param str display_name: The name displayed to the user.
        :param str ip_address: The ip address of the virtual server.
        :param list[str] ports: The list of single ports or port ranges that this virtual server will balance through.
        :param str pool_path: URL path of the Load balancer pool associated with this virtual server.
        :param set[str] tags: The tenant tags associated to the virtual server.
        :param bool enabled: If True, the virtual server is enabled.
        """
        VServer.__init__(self, id, display_name, ip_address, ports, tags=tags, enabled=enabled)
        self.pool_path = pool_path

    def is_declarative(self):
        return True

    def get_pool_path(self):
        return self.pool_path

    def get_pool_update_path(self):
        return self.get_pool_path()

    @classmethod
    def from_json(cls, raw_json):
        return VServerDeclarative(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            ip_address=raw_json[_IP_ADDRESS_KEY],
            ports=raw_json[_PORTS_KEY],
            tags=cls._parse_tags(raw_json[_TAGS_KEY]) if _TAGS_KEY in raw_json else set(),
            enabled=raw_json[_ENABLED_KEY],
            pool_path=raw_json[_POOL_KEY],
        )
