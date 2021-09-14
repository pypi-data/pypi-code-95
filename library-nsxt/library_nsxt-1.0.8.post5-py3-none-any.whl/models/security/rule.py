from library_nsxt.models.security import NSXTSecurityModel

_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_DESCRIPTION_KEY = "description"
_SERVICES_KEY = "services"
_CONNECT_FROM_KEY = "source_groups"
_CONNECT_TO_KEY = "destination_groups"
_RESOURCE_TYPE_KEY = "resource_type"
_PARENT_PATH_KEY = "parent_path"
_PATH_KEY = "path"
_SCOPE_KEY = "scope"
_ACTION_KEY = "action"
_LOGGED_KEY = "logged"
_REVISION_KEY = "_revision"

_TENANT_URL_INDEX = -3
_POLICY_URL_INDEX = -1
_PARENT_PATH_TEMPLATE = "/infra/domains/%s/security-policies/%s"
_SELF_PATH_TEMPLATE = "%s/rules/%s"

_SERVICE_URL_INDEX = -1
_CONNECTION_URL_INDEX = -1
_SERVICE_URL_PATH_FORMAT = "/infra/services/%s"
_CONNECTION_URL_PATH_FORMAT = "/infra/domains/%s/groups/%s"
_RESOURCE_TYPE_RULE = "Rule"
_ACTION_DEFAULT = "ALLOW"
_LOGGED_DEFAULT = False


class Rule(NSXTSecurityModel):
    """Comparison model for the NSX-T Policy Rule object"""

    def __init__(self, id, display_name, policy, tenant="default", connect_from=None, connect_to=None, services=["ANY"],
                 description=None, revision=None):
        """
        Generates a new Rule model object.

        :param str id: The internal id of the rule.
        :param str display_name: The name displayed to the user.
        :param str policy: The name of the policy that this rule belongs to.
        :param str tenant: The owner of the rule. Default is "default"
        :param set[str] connect_from: The set of groups that are the source of the connection.
        :param set[str] connect_to: The set of groups that are the destination of the connection.
        :param set[str] services: The set of services that are allowed in the connection.
        :param str description: The optional description of the rule.
        :param int revision: The internal revision number of the rule in the NSX-T API.
        """
        NSXTSecurityModel.__init__(self, id, display_name, self.__build_parent_path(tenant, policy), revision)
        self.tenant = tenant
        self.policy = policy
        self.connect_from = connect_from if connect_from is not None else set()
        self.connect_to = connect_to if connect_to is not None else set()
        self.services = services if services is not None else set()
        self.description = description
        self.__original_parent_path = self.__build_parent_path(tenant, policy)
        self.__original_id = id

    def get_original_path(self):
        return _SELF_PATH_TEMPLATE % (self.__original_parent_path, self.__original_id)

    def get_path(self):
        return _SELF_PATH_TEMPLATE % (self.__build_parent_path(self.tenant, self.policy), self.id)

    def to_json(self):
        connections_from = self.__get_connection_address(self.connect_from, self.tenant)
        connections_to = self.__get_connection_address(self.connect_to, self.tenant)
        output = {
            _ID_KEY: self.id,
            _DISPLAY_NAME_KEY: self.display_name,
            _PATH_KEY: self.get_path(),
            _PARENT_PATH_KEY: self.get_parent_path(),
            "relative_path":  self.id,
            _SERVICES_KEY: self.__get_service_address(self.services),
            _CONNECT_FROM_KEY: connections_from,
            _CONNECT_TO_KEY: connections_to,
            _SCOPE_KEY: self.__get_scope(connections_from, connections_to),
            _RESOURCE_TYPE_KEY: _RESOURCE_TYPE_RULE,
            _ACTION_KEY: _ACTION_DEFAULT,
            _LOGGED_KEY: _LOGGED_DEFAULT
        }

        if self.description is not None:
            output[_DESCRIPTION_KEY] = self.description

        if self.revision is not None:
            output[_REVISION_KEY] = self.revision

        return output

    @classmethod
    def from_json(cls, raw_json):
        return Rule(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            tenant=cls.__parse_tenant(raw_json[_PARENT_PATH_KEY], raw_json[_DISPLAY_NAME_KEY]),
            policy=cls.__parse_policy(raw_json[_PARENT_PATH_KEY], raw_json[_DISPLAY_NAME_KEY]),
            connect_from=cls.__parse_connections(raw_json[_CONNECT_FROM_KEY], raw_json[_DISPLAY_NAME_KEY]),
            connect_to=cls.__parse_connections(raw_json[_CONNECT_TO_KEY], raw_json[_DISPLAY_NAME_KEY]),
            services=cls.__parse_services(raw_json[_SERVICES_KEY], raw_json[_DISPLAY_NAME_KEY]),
            description=raw_json[_DESCRIPTION_KEY] if _DESCRIPTION_KEY in raw_json else None,
            revision=raw_json[_REVISION_KEY] if _REVISION_KEY in raw_json else None
        )

    @staticmethod
    def __parse_tenant(raw_tenant, display_name):
        """
        Validates and formats the loaded tenant of the rule.

        :param str raw_tenant: The raw tenant.
        :return: The parsed tenant.
        :rtype: str
        :raises ValueError: If it's not described in URL form.
        """
        if "/" not in raw_tenant:
            raise ValueError("Connection [%s]: remote tenant must be in url path form" % display_name)
        else:
            return raw_tenant.split("/")[_TENANT_URL_INDEX]

    @staticmethod
    def __parse_policy(raw_policy, display_name):
        """
        Validates and formats the parent policy of the rule.

        :param raw_policy: The raw policy.
        :return: The parsed policy.
        :raises ValueError: If it's not described in URL form.
        """
        if "/" not in raw_policy:
            raise ValueError("Connection [%s]: remote policy must be in url path form" % display_name)
        else:
            return raw_policy.split("/")[_POLICY_URL_INDEX]

    @staticmethod
    def __parse_services(raw_service_list, display_name):
        """
        Validates and formats the loaded services of the rule.

        :param list[str] raw_service_list: The raw service list.
        :return: The parsed service set.
        :rtype: set[str]
        :raises ValueError: If it's not any and it's not described in URL form.
        """
        if any([service.lower() == "any" for service in raw_service_list]):
            return {"ANY"}
        if any(["/" not in service_path for service_path in raw_service_list]):
            raise ValueError("Connection [%s]: remote service list must be in url path form" % display_name)
        else:
            return {service_path.split("/")[_SERVICE_URL_INDEX] for service_path in raw_service_list}

    @staticmethod
    def __parse_connections(raw_connection_list, display_name):
        """
        Validates and formats the loaded connections of the rule. Both sources and destinations.

        :param list[str] raw_connection_list: The raw connection list.
        :return: The parsed connection set.
        :rtype: set[str]
        :raises ValueError: If it's not any and it's not described in URL form.
        """
        if any([connection.lower() == "any" for connection in raw_connection_list]):
            return {"ANY"}
        if any(["/" not in connection_path for connection_path in raw_connection_list]):
            raise ValueError("Connection [%s]: remote connection list must be in url path form" % display_name)
        else:
            return {connection_path.split("/")[_CONNECTION_URL_INDEX] for connection_path in raw_connection_list}

    @staticmethod
    def __get_service_address(service_set):
        """
        Sets the full path address for every service on the list. Also handles ANY.

        :param set[str] service_set: The raw services.
        :return: The parsed services as a list.
        :rtype: list[str]
        """
        if any([service.lower() == "any" for service in service_set]):
            return ["ANY"]
        else:
            return [_SERVICE_URL_PATH_FORMAT % service for service in service_set]

    @staticmethod
    def __get_connection_address(raw_connection_list, tenant):
        """
        Sets the full path address for every connection on the list. Also handles ANY.

        :param raw_connection_list: The raw connection groups list.
        :param tenant: The tenant or domain of the groups.
        :return: The parsed connections as a list.
        """
        if any([connection.lower() == "any" for connection in raw_connection_list]):
            return ["ANY"]
        else:
            return [_CONNECTION_URL_PATH_FORMAT % (tenant, connection) for connection in raw_connection_list]

    @staticmethod
    def __get_scope(conn_from_list, conn_to_list):
        """
        Returns the connections scope, based on the source and destination connections. Also handles ANY.

        :param list[str] conn_from_list: The source connection groups list.
        :param list[str] conn_to_list: The destination connection groups list.
        :return: The resulting scope as a list.
        :rtype: list[str]
        """
        if "ANY" in conn_from_list or "ANY" in conn_to_list:
            return ["ANY"]
        else:
            return list(set(conn_from_list) | set(conn_to_list))

    @staticmethod
    def __build_parent_path(tenant, policy):
        """
        Auxiliary method to generate the parent path for a given tenant.

        :param str tenant: The rule's tenant
        :return: The generated parent path
        :rtype: str
        """
        return _PARENT_PATH_TEMPLATE % (tenant, policy)
