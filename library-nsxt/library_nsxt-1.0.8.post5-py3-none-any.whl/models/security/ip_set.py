from library_nsxt.models.security import NSXTSecurityModel

_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_DESCRIPTION_KEY = "description"
_TAGS_KEY = "tags"
_IP_ADDRESSES_KEY = "ip_addresses"
_RESOURCE_TYPE_KEY = "resource_type"
_REVISION_KEY = "_revision"

_IPSET_PARENT_PATH = "/ip-sets"
_SELF_PATH_TEMPLATE = "%s/%s"
_RESOURCE_TYPE_IP_SET = "IPSet"


class IPSet(NSXTSecurityModel):
    """Comparison model for the NSX-T IP Set object"""

    def __init__(self, id, display_name, tags=None, ip_addresses=None, description=None, revision=None):
        """
        Generates a new IP set model object.

        :param str id: The internal id of the IP set.
        :param str display_name: The name displayed to the user.
        :param set[(str, str)] tags: The set of tags that apply to this ip set.
        :param set[str] ip_addresses: The set of IP addresses that conform this ip set.
        :param str description: The optional description of the IP set.
        :param int revision: The internal revision number of the IP set in the NSX-T API.
        """
        NSXTSecurityModel.__init__(self, id, display_name, _IPSET_PARENT_PATH, None)
        self.tags = tags if tags is not None else set()
        self.ip_addresses = ip_addresses if ip_addresses is not None else set()
        self.description = description
        self.revision = revision
        self.__original_parent_path = _IPSET_PARENT_PATH
        self.__original_id = id

    def get_original_path(self):
        return _SELF_PATH_TEMPLATE % (self.__original_parent_path, self.__original_id)

    def get_path(self):
        return _SELF_PATH_TEMPLATE % (self.parent_path, self.id)

    def to_json(self):
        output = {
            _ID_KEY: self.id,
            _DISPLAY_NAME_KEY: self.display_name,
            _TAGS_KEY: IPSet._build_tags(self.tags),
            _IP_ADDRESSES_KEY: list(self.ip_addresses),
            _RESOURCE_TYPE_KEY: _RESOURCE_TYPE_IP_SET,
        }

        if self.description is not None:
            output[_DESCRIPTION_KEY] = self.description

        if self.revision is not None:
            output[_REVISION_KEY] = self.revision

        return output

    @classmethod
    def from_json(cls, raw_json):
        return IPSet(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            tags=cls._parse_tags(raw_json[_TAGS_KEY]) if _TAGS_KEY in raw_json else set(),
            ip_addresses=set(raw_json[_IP_ADDRESSES_KEY]),
            description=raw_json[_DESCRIPTION_KEY] if _DESCRIPTION_KEY in raw_json else None,
            revision=raw_json[_REVISION_KEY] if _REVISION_KEY in raw_json else None
        )
