from library_nsxt.models import NSXTModel

_ID_KEY = "external_id"
_DISPLAY_NAME_KEY = "display_name"
_TAGS_KEY = "tags"
_INFO_KEY = "guest_info"
_OS_KEY = "os_name"


class VMachine(NSXTModel):
    """Comparison model for the NSX-T Virtual Machine object"""

    def __init__(self, id, display_name, tags=None, os=None):
        """
        Generates a new Virtual Machine model object.

        :param str id: The internal id of the vm.
        :param str display_name: The name displayed to the user.
        :param set[(str, str)] tags: The tags that apply to this vm.
        :param str os: The optional os of the vm.
        """
        NSXTModel.__init__(self, id, display_name, None)
        self.tags = tags if tags is not None else set()
        self.os = os

    def to_json(self):
        return {
            _ID_KEY: self.id,
            _TAGS_KEY: self._build_tags(self.tags)
        }

    @classmethod
    def from_json(cls, raw_json):
        return VMachine(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            tags=cls._parse_tags(raw_json[_TAGS_KEY]) if _TAGS_KEY in raw_json else set(),
            os=raw_json[_INFO_KEY][_OS_KEY] if _OS_KEY in raw_json[_INFO_KEY] else None
        )
