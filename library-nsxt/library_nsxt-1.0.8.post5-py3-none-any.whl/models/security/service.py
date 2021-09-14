from library_nsxt.models.security import NSXTSecurityModel

_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_DESCRIPTION_KEY = "description"
_DEFINITION_KEY = "service_entries"
_RESOURCE_TYPE_KEY = "resource_type"
_REVISION_KEY = "_revision"

_SERVICE_PARENT_PATH = "/infra"
_SELF_PATH_TEMPLATE = "%s/services/%s"
_RESOURCE_TYPE_SERVICE = "Service"

_ENTRY_ID_KEY = "id"
_ENTRY_NAME_KEY = "display_name"
_ENTRY_PROTOCOL_KEY = "protocol"
_ENTRY_PORTS_KEY = "ports"
_ENTRY_L4_PROTOCOL_KEY = "l4_protocol"
_ENTRY_SRC_PORTS_KEY = "source_ports"
_ENTRY_DST_PORTS_KEY = "destination_ports"
_ENTRY_RESOURCE_TYPE_KEY = "resource_type"
_ENTRY_REVISION_KEY = "_revision"

_ICMP_MATCHER = "icmp"
_ICMP_IDENTIFIER = "ICMP"
_ICMP_TYPE_KEY = "icmp_type"
_ICMP_RESOURCE_TYPE = "ICMPTypeServiceEntry"

_IGMP_MATCHER = "igmp"
_IGMP_IDENTIFIER = "IGMP"
_IGMP_RESOURCE_TYPE = "IGMPTypeServiceEntry"


class Service(NSXTSecurityModel):
    """Comparison model for the NSX-T Service object"""

    def __init__(self, id, display_name, definition=None, description=None, revision=None):
        """
        Generates a new Service model object.

        :param str id: The internal id of the rule.
        :param str display_name: The name displayed to the user.
        :param dict[str, dict[str, str or int]] definition: The full definition of the service, as shown in the
                                                            *from_json* and *to_json* methods.
        :param str description: The optional description of the rule.
        """
        NSXTSecurityModel.__init__(self, id, display_name, _SERVICE_PARENT_PATH, revision)
        self.definition = definition if definition is not None else {}
        self.description = description
        self.__original_id = id

    def get_original_path(self):
        return _SELF_PATH_TEMPLATE % (_SERVICE_PARENT_PATH, self.__original_id)

    def get_path(self):
        return _SELF_PATH_TEMPLATE % (self.parent_path, self.id)

    def to_json(self):
        output = {
            _ID_KEY: self.id,
            _DISPLAY_NAME_KEY: self.display_name,
            _DEFINITION_KEY: self.__build_remote_definition_entries(self.definition),
            _RESOURCE_TYPE_KEY: _RESOURCE_TYPE_SERVICE
        }

        if self.description is not None:
            output[_DESCRIPTION_KEY] = self.description

        if self.revision is not None:
            output[_REVISION_KEY] = self.revision

        return output

    @classmethod
    def from_json(cls, raw_json):
        return Service(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            definition=cls.__parse_definition_entries(raw_json[_DEFINITION_KEY]),
            description=raw_json[_DESCRIPTION_KEY] if _DESCRIPTION_KEY in raw_json else None,
            revision=raw_json[_REVISION_KEY] if _REVISION_KEY in raw_json else None
        )

    @staticmethod
    def __parse_definition_entries(raw_definitions):
        """
        Decouples remote definition objects into name, protocol, port. Some special definitions, like ICMP, do not
        have protocol or port.

        :param list[dict] raw_definitions: The raw definition of the service.
        :return: A dictionary with the name of the service as a key, and its protocol, revision and port as the value.
        :rtype: dict[str, dict[str, str or int]]
        :raises ValueError: If a definition cannot be parsed.
        """
        definitions = {}
        for entry in raw_definitions:
            revision = entry[_ENTRY_REVISION_KEY] if _ENTRY_REVISION_KEY in entry else None
            if entry[_RESOURCE_TYPE_KEY] == _ICMP_RESOURCE_TYPE:
                definitions[_ICMP_IDENTIFIER] = {_ENTRY_REVISION_KEY: revision}
            elif entry[_RESOURCE_TYPE_KEY] == _IGMP_RESOURCE_TYPE:
                definitions[_IGMP_IDENTIFIER] = {_ENTRY_REVISION_KEY: revision}
            else:
                ports = set(entry[_ENTRY_DST_PORTS_KEY])
                definitions[entry[_ENTRY_ID_KEY]] = {_ENTRY_PROTOCOL_KEY: entry[_ENTRY_L4_PROTOCOL_KEY],
                                                     _ENTRY_PORTS_KEY: ports,
                                                     _ENTRY_REVISION_KEY: revision}
        return definitions

    @staticmethod
    def __build_remote_definition_entries(remote_definitions):
        """
        Creates the service entries that define the service from the definitions and the revisions.

        :param dict[str, dict[str, str or int]] remote_definitions: The service definition.
        :return: A list of objects as expected by the remote device.
        :rtype: list[dict]
        """
        definitions = []
        for service_name, service_def in remote_definitions.items():
            if service_name.lower() == _ICMP_MATCHER:
                icmp_entries = Service.__build_icmp_entries(service_def[_ENTRY_REVISION_KEY])
                definitions.extend(icmp_entries)
            elif service_name == _IGMP_MATCHER:
                igmp_entry = Service.__build_igmp_entry(service_def[_ENTRY_REVISION_KEY])
                definitions.append(igmp_entry)
            else:
                srv_entry = {_ENTRY_NAME_KEY: service_name}
                srv_entry.update(service_def)
                entry = Service.__build_service_entry(srv_entry, service_def[_ENTRY_REVISION_KEY])
                definitions.append(entry)
        return definitions

    @staticmethod
    def __build_icmp_entries(revision=None):
        """
        Creates the ICMP entries with an optional revision number.

        :param int or None revision: The optional revision number. Default is None.
        :return: A service entry as expected by the remote device.
        :rtype: list[dict]
        """
        icmp_request = {
            _ENTRY_ID_KEY: "ICMP_Echo_Request",
            _ENTRY_NAME_KEY: "ICMP_Echo_Request",
            _ENTRY_PROTOCOL_KEY: "ICMPv4",
            _ENTRY_RESOURCE_TYPE_KEY: _ICMP_RESOURCE_TYPE,
            _ICMP_TYPE_KEY: 8
        }
        icmp_response = {
            _ENTRY_ID_KEY: "ICMP_Echo_Reply",
            _ENTRY_NAME_KEY: "ICMP_Echo_Reply",
            _ENTRY_PROTOCOL_KEY: "ICMPv4",
            _ENTRY_RESOURCE_TYPE_KEY: _ICMP_RESOURCE_TYPE,
            _ICMP_TYPE_KEY: 0
        }

        if revision is not None:
            icmp_request[_ENTRY_REVISION_KEY] = revision
            icmp_response[_ENTRY_REVISION_KEY] = revision

        return [icmp_request, icmp_response]

    @staticmethod
    def __build_igmp_entry(revision=None):
        """
        Creates the IGMP entry with an optional revision number.

        :param int or None revision: The optional revision number. Default is None.
        :return: A service entry as expected by the remote device.
        :rtype: dict
        """
        igmp_membership = {
            _ENTRY_ID_KEY: "IGMP_Membership_Query",
            _ENTRY_NAME_KEY: "IGMP_Membership_Query",
            _ENTRY_RESOURCE_TYPE_KEY: _IGMP_RESOURCE_TYPE,
        }

        if revision is not None:
            igmp_membership[_ENTRY_REVISION_KEY] = revision

        return igmp_membership

    @staticmethod
    def __build_service_entry(entry, revision=None):
        """
        Creates the entry with an optional revision number.

        :param int or None revision: The optional revision number. Default is None.
        :return: A service entry as expected by the remote device.
        :rtype: dict
        """
        remote_entry = {
            _ENTRY_ID_KEY: entry[_ENTRY_NAME_KEY],
            _ENTRY_NAME_KEY: entry[_ENTRY_NAME_KEY],
            _ENTRY_L4_PROTOCOL_KEY: entry[_ENTRY_PROTOCOL_KEY],
            _ENTRY_SRC_PORTS_KEY: [],
            _ENTRY_DST_PORTS_KEY: list(entry[_ENTRY_PORTS_KEY]),
            _ENTRY_RESOURCE_TYPE_KEY: "L4PortSetServiceEntry"
        }
        if revision is not None:
            remote_entry[_ENTRY_REVISION_KEY] = revision
        return remote_entry
