"""
Binary tests regarding the health of a specific component.
To be used by both health rules and failover tests.
"""

PATHS_PER_VOLUME = 12


def is_volume_connected(volume_component):
    return volume_component.number_of_active_paths == PATHS_PER_VOLUME


def is_mgmt_ip_matching_role(role_component):
    # 9.151.140.12(?) == 'dde(?)-BOOT'
    def get_mgmt_ip_id(ip):
        return int(ip[-1])

    return get_mgmt_ip_id(role_component.management_ip) == role_component.role_id
