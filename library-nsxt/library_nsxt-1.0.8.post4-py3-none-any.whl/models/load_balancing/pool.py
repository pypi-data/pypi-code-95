from library_nsxt.models import NSXTModel

_ID_KEY = "id"
_DISPLAY_NAME_KEY = "display_name"
_RESOURCE_TYPE_KEY = "resource_type"
_MEMBERS_KEY = "members"

_ADMIN_STATE_KEY = "admin_state"
_IP_ADDRESS_KEY = "ip_address"
_WEIGHT_KEY = "weight"
_BACKUP_MEMBER_KEY = "backup_member"


class PoolMember:
    """Model for the NSX-T PoolMember"""

    def __init__(self, admin_state, ip_address, weight, backup_member, display_name):
        """
        Generates a load balancer pool member.

        :param str admin_state: The admin state of the pool member. Can be `ENABLED`, `DISABLED` or `GRACEFUL_DISABLED`
        :param str ip_address: The IP address of the pool member.
        :param int weight: The current weight being balanced through this member.
        :param bool backup_member: If True, this pool member is the backup for the pool.
        :param str display_name: The name displayed to the user.
        """
        self.display_name = display_name
        self.ip_address = ip_address
        self.weight = weight
        self.admin_state = admin_state
        self.backup_member = backup_member

    def to_json(self):
        return {
            _ADMIN_STATE_KEY: self.admin_state,
            _IP_ADDRESS_KEY: self.ip_address,
            _WEIGHT_KEY: self.weight,
            _DISPLAY_NAME_KEY: self.display_name
        }

    @classmethod
    def from_json(cls, raw_json):
        return PoolMember(
            admin_state=raw_json[_ADMIN_STATE_KEY],
            ip_address=raw_json[_IP_ADDRESS_KEY],
            weight=raw_json[_WEIGHT_KEY],
            backup_member=raw_json[_BACKUP_MEMBER_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY]
        )


class Pool(NSXTModel):
    """Model for the NSX-T Pool"""

    def __init__(self, id, display_name, resource_type, members):
        """
        Generates a new Load balancer pool object.

        :param str id: The internal id of the pool.
        :param str display_name: The name displayed to the user.
        :param str resource_type: The internal resource type of the pool.
        :param list[PoolMember] members: The members of the pool.
        """
        NSXTModel.__init__(self, id, display_name, revision=None)
        self.resource_type = resource_type
        self.members = members

    @classmethod
    def from_json(cls, raw_json):
        return Pool(
            id=raw_json[_ID_KEY],
            display_name=raw_json[_DISPLAY_NAME_KEY],
            resource_type=raw_json[_RESOURCE_TYPE_KEY],
            members=cls.__parse_member(raw_json[_MEMBERS_KEY])
        )

    def to_json(self):
        output = {
            _ID_KEY: self.id,
            _DISPLAY_NAME_KEY: self.display_name,
            _RESOURCE_TYPE_KEY: self.resource_type,
            _MEMBERS_KEY: [member.to_json() for member in self.members],
        }
        return output

    @staticmethod
    def __parse_member(expresion):
        """
        Parses the members of the Load balancer pool to python objects.

        :param dict expresion: The raw expresion declaration.
        :return: The parsed list of members.
        :rtype: list[PoolMember]
        """
        members = [PoolMember.from_json(member) for member in expresion]
        return members
