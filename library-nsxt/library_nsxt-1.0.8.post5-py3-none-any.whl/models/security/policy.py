from library_nsxt.models.security import NSXTSecurityModel

_ID_KEY = "id"
_NAME_KEY = "display_name"
_DESC_KEY = "description"
_CATEGORY_KEY = "category"
_RESOURCE_TYPE_KEY = "resource_type"
_PATH_KEY = "parent_path"
_REVISION_KEY = "_revision"

_TENANT_URL_INDEX = -1
_PARENT_PATH_TEMPLATE = "/infra/domains/%s"
_SELF_PATH_TEMPLATE = "%s/security-policies/%s"

_RESOURCE_TYPE_POLICY = "SecurityPolicy"


class Policy(NSXTSecurityModel):
    """Comparison model for the NSX-T Security Policy object"""

    def __init__(self, id, display_name, category="Application", tenant="default", description=None, revision=None):
        """
        Generates a new Policy model object.

        :param str id: The internal id of the policy.
        :param str display_name: The name displayed to the user.
        :param str category: The category of the Policy. Can be `Application`, `Environment` or `Infrastructure`. The
                             order of application of the firewall configuration depends on the order of categories.
        :param str tenant: The owner of the policy. Default is "default"
        :param str description: The optional description of the policy.
        :param int revision: The internal revision number of the policy in the NSX-T API.
        """
        NSXTSecurityModel.__init__(self, id, display_name, self.__build_parent_path(tenant), revision)
        self.category = self.__parse_category(category, display_name)
        self.tenant = tenant
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
            _NAME_KEY: self.display_name,
            _DESC_KEY: self.description,
            _CATEGORY_KEY: self.category,
            _RESOURCE_TYPE_KEY: _RESOURCE_TYPE_POLICY
        }

        if self.description is not None:
            output[_DESC_KEY] = self.description

        if self.revision is not None:
            output[_REVISION_KEY] = self.revision

        return output

    @classmethod
    def from_json(cls, raw_json):
        return Policy(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_NAME_KEY],
            category=raw_json[_CATEGORY_KEY],
            tenant=cls.__parse_tenant(raw_json[_PATH_KEY], raw_json[_NAME_KEY]),
            description=raw_json[_DESC_KEY] if _DESC_KEY in raw_json else None,
            revision=raw_json[_REVISION_KEY] if _REVISION_KEY in raw_json else None
        )

    @staticmethod
    def __parse_category(raw_category, display_name):
        """
        Validates and formats the scope from any source.

        :param str raw_category: The raw category.
        :return: The parsed category.
        :rtype: str
        :raises ValueError: If the category is not one of the valid categories.
        """
        if raw_category.lower() == 'ethernet':
            return "Ethernet"
        elif raw_category.lower() == 'emergency':
            return "Emergency"
        elif raw_category.lower() == 'environment':
            return "Environment"
        elif raw_category.lower() == 'infrastructure':
            return "Infrastructure"
        elif raw_category.lower() == 'application':
            return "Application"
        else:
            raise ValueError("Application [%s]: scope does not have a valid value" % display_name)

    @staticmethod
    def __parse_tenant(parent_path, display_name):
        """
        Validates and formats the tenant from the policy parent path.

        :param str parent_path: The raw parent path url.
        :return: The policy tenant.
        :rtype: str
        :raises ValueError: If the url path is not valid.
        """
        if "/" not in parent_path:
            raise ValueError("Application [%s]: remote tenant must be in url path form" % display_name)
        else:
            return parent_path.split("/")[_TENANT_URL_INDEX]

    @staticmethod
    def __build_parent_path(tenant):
        """
        Auxiliary method to generate the parent path for a given tenant.

        :param str tenant: The policy's tenant
        :return: The generated parent path
        :rtype: str
        """
        return _PARENT_PATH_TEMPLATE % tenant
