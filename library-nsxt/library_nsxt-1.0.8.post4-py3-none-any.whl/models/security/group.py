from library_nsxt.models.security import NSXTSecurityModel

_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_DESCRIPTION_KEY = "description"
_EXPRESSION_KEY = "expression"
_TAG_KEY = "value"
_PATH_KEY = "parent_path"
_REVISION_KEY = "_revision"

_TENANT_URL_INDEX = -1
_PARENT_PATH_TEMPLATE = "/infra/domains/%s"
_SELF_PATH_TEMPLATE = "%s/groups/%s"

_DEFAULT_EXPRESSION_SCOPE = "security"


class Group(NSXTSecurityModel):
    """Comparison model for the NSX-T Group object"""

    def __init__(self, id, display_name, tag_name, tenant="default", description=None, revision=None):
        """
        Generates a new Group model object.

        :param str id: The internal id of the group.
        :param str display_name: The name displayed to the user.
        :param str tag_name: The tag that will identify this group.
        :param str tenant: The owner of the group. Default is "default"
        :param str description: The optional description of the group.
        :param int revision: The internal revision number of the group in the NSX-T API.
        """
        NSXTSecurityModel.__init__(self, id, display_name, self.__build_parent_path(tenant), revision)
        self.tenant = tenant
        self.tag_name = tag_name
        self.description = description
        self.__original_parent_path = self.__build_parent_path(tenant)
        self.__original_id = id

    def get_original_path(self):
        return _SELF_PATH_TEMPLATE % (self.__original_parent_path, self.__original_id)

    def get_path(self):
        return _SELF_PATH_TEMPLATE % (self.__build_parent_path(self.tenant), self.id)

    def to_json(self):
        output = {
            _ID_KEY: self.id,
            _DISPLAY_NAME_KEY: self.display_name
        }

        if self.description is not None:
            output[_DESCRIPTION_KEY] = self.description

        if self.tag_name is not None:
            output[_EXPRESSION_KEY] = self.__generate_expresion(self.tag_name)

        if self.revision is not None:
            output[_REVISION_KEY] = self.revision

        return output

    @classmethod
    def from_json(cls, raw_json):
        return Group(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            tenant=cls.__parse_tenant(raw_json[_PATH_KEY], raw_json[_DISPLAY_NAME_KEY]),
            tag_name=cls.__parse_tag(raw_json[_EXPRESSION_KEY]),
            description=raw_json[_DESCRIPTION_KEY] if _DESCRIPTION_KEY in raw_json else None,
            revision=raw_json[_REVISION_KEY] if _REVISION_KEY in raw_json else None
        )

    @staticmethod
    def __parse_tenant(parent_path, display_name):
        """
        Validates and formats the loaded tenant from the model's parent path.

        :param str parent_path: The raw URL parent path of the model.
        :return: The tenant of the model.
        :rtype: str
        :raises ValueError: If the parent path is not in URL form.
        """
        if "/" not in parent_path:
            raise ValueError("Group [%s]: Remote tenant must be in parent path" % display_name)
        else:
            return parent_path.split("/")[_TENANT_URL_INDEX]

    @staticmethod
    def __parse_tag(expresion):
        """
        Extracts the tag name from the group declaration in the device.

        :param dict expresion: The raw expresion declaration.
        :return: The parsed tag name.
        :rtype: str
        :raises ValueError: If the expresion is not in the expected format.
        """
        tag_values = [member[_TAG_KEY] for member in expresion if _TAG_KEY in member]
        if len(tag_values) == 0 or any(["|" not in tag for tag in tag_values]):
            return None
        else:
            return tag_values[0].split("|")[1]

    @staticmethod
    def __generate_expresion(tag_name):
        """
        Generates the expresion as expected by the NSX-T API.

        :param str tag_name: The tag name for ip sets and virtual machines.
        :return: The expected group expresion.
        :rtype: dict
        """
        tag_string = "%s|%s" % (_DEFAULT_EXPRESSION_SCOPE, tag_name)
        return [
            {
                "member_type": "VirtualMachine",
                "key": "Tag",
                "operator": "EQUALS",
                "value": tag_string,
                "resource_type": "Condition"
            },
            {
                "conjunction_operator": "OR",
                "resource_type": "ConjunctionOperator"
            },
            {
                "member_type": "IPSet",
                "key": "Tag",
                "operator": "EQUALS",
                "value": tag_string,
                "resource_type": "Condition"
            },
            {
                "conjunction_operator": "OR",
                "resource_type": "ConjunctionOperator"
            },
            {
                "member_type": "LogicalSwitch",
                "key": "Tag",
                "operator": "EQUALS",
                "value": tag_string,
                "resource_type": "Condition"
            }
        ]

    @staticmethod
    def __build_parent_path(tenant):
        """
        Auxiliary method to generate the parent path for a given tenant.

        :param str tenant: The group's tenant
        :return: The generated parent path
        :rtype: str
        """
        return _PARENT_PATH_TEMPLATE % tenant
