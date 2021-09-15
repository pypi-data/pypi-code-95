import os
from .api_client import APIClientBase


class Protection(APIClientBase):
    def __init__(self, url_base=None, **kwargs):
        super().__init__(url_base or os.environ.get("PROTECTION_SERVICE", ""), **kwargs)

    def get_policies(self):
        return self.get_request("/policies")

    def get_policy(self, id):
        return self.get_request("/policies/{id}", id=id)

    def create_policy(self, policy_name: str, pool_name: str = None, alert_enabled: bool = True, rules: list = None):
        body = {
            "policyName": policy_name,
            "poolName": pool_name,
            "alertEnabled": alert_enabled,
            "rules": rules or [],
        }
        return self.post_request("/policies", body=body)

    def patch_policy(
        self, id: str, policy_name: str = None, pool_name: str = None, alert_enabled: bool = None, rules: list = None
    ):
        body = {}

        if policy_name is not None:
            body["policyName"] = policy_name
        if pool_name is not None:
            body["poolName"] = pool_name
        if alert_enabled is not None:
            body["alertEnabled"] = alert_enabled
        if rules is not None:
            body["rules"] = rules

        return self.patch_request("/policies/{id}", id=id, body=body)

    def delete_policy(self, id):
        return self.get_request("/policies/{id}", id=id)

    def get_replication_hosts(self):
        return self.get_request("/hosts")

    def get_replication_host(self, id):
        return self.get_request("/hosts/{id}", id=id)

    def create_replication_host(self, body):
        return self.post_request("/hosts", body=body)

    def delete_replication_host(self, id):
        return self.delete_request("/hosts/{id}", id=id)

    def patch_replication_host(self, id, body):
        return self.patch_request("/hosts/{id}", id=id, body=body)

    def get_protected_vms(self):
        return self.get_request("/vms")

    def get_protected_vm(self, vm_syn_id: str):
        return self.get_request("/vms/{vm_syn_id}", vm_syn_id=vm_syn_id)

    def create_external_vm_protection_job(self, config):
        body = {"config": config}
        return self.post_request("/jobs/protect-external-vm", body=body)

    def create_local_vm_protection_job(self, config):
        body = {"config": config}
        return self.post_request("/jobs/protect-local-vm", body=body)

    def create_local_vm_replication_job(self, config):
        body = {"config": config}
        return self.post_request("/jobs/replicate-local-vm", body=body)

    def get_replication_hosts(self):
        return self.get_request("/hosts")

    def get_replication_host(self, id):
        return self.get_request("/hosts/{}", id)

    def create_replication_host(
        self,
        host: str,
        name: str,
        password: str,
        is_encrpypted: bool,
        bandwidth_limit_value: int,
        bandwidth_limit_start_time: str,
        bandwidth_limit_stop_time: str,
    ):
        """Creates a replication host

        bandwidth_limit_value is in bytes
        bandwidth_limit_start_time format is HHMMSS'Z', the time should always use UTC timezone.
        bandwidth_limit_stop_time format is HHMMSS'Z', the time should always use UTC timezone.
        bandwidth_limit_start_time and bandwidth_limit_stop_time time interval is when the
        replication bandwidth will be limited to the bandwidth_limit_value.
        Example:
        bandwidth_limit_value: 50000,
        bandwidth_limit_start_time: 090000Z,
        bandwidth_limit_stop_time: 163000Z,
        The effect of these values is that between 9 AM UTC and 4:30 PM UTC
        the replication bandwidth will be limited to 50KB.
        """

        payload = {
            "host": host,
            "name": name,
            "password": password,
            "is_encrypted": is_encrpypted,
            "bandwidth_limits": [
                {
                    "limit": bandwidth_limit_value,
                    "start_time": {
                        "value": bandwidth_limit_start_time,
                        "type": "timeOfDay",
                    },
                    "stop_time": {
                        "value": bandwidth_limit_stop_time,
                        "type": "timeOfDay",
                    },
                }
            ],
        }
        return self.post_request("/hosts/", body=payload)

    def remove_replication_host(self, id):
        return self.delete_request("/hosts/{id}")

    def patch_replication_host(
        self,
        id,
        host: str = None,
        name: str = None,
        password: str = None,
        is_encrypted: bool = None,
        bandwidth_limit_value: int = None,
        bandwidth_limit_start_time: str = None,
        bandwidth_limit_stop_time: str = None,
    ):
        """Updates a replication host

        bandwidth_limit_value is in bytes
        bandwidth_limit_start_time format is HHMMSS'Z', the time should always use UTC timezone.
        bandwidth_limit_stop_time format is HHMMSS'Z', the time should always use UTC timezone.
        bandwidth_limit_start_time and bandwidth_limit_stop_time time interval is when the
        replication bandwidth will be limited to the bandwidth_limit_value.
        Example:
        bandwidth_limit_value: 50000,
        bandwidth_limit_start_time: 090000Z,
        bandwidth_limit_stop_time: 163000Z,
        The effect of these values is that between 9 AM UTC and 4:30 PM UTC
        the replication bandwidth will be limited to 50KB.
        In order to update a replication host's bandwidth limit values you must include a value for
        bandwidth_limit_value, bandwidth_limit_start_time and bandwidth_limit_stop_time, if one of them
        is not included the bandwidth limit will not be updated
        """
        payload = {}
        if host is not None:
            payload["host"] = host
        if name is not None:
            payload["name"] = name
        if password is not None:
            payload["password"] = password
        if is_encrypted is not None:
            payload["is_encrypted"] = is_encrypted
        if (
            bandwidth_limit_value is not None
            and bandwidth_limit_start_time is not None
            and bandwidth_limit_value is not None
        ):
            payload["bandwidth_limits"] = [
                {
                    "limit": bandwidth_limit_value,
                    "start_time": {
                        "value": bandwidth_limit_start_time,
                        "type": "timeOfDay",
                    },
                    "stop_time": {
                        "value": bandwidth_limit_stop_time,
                        "type": "timeOfDay",
                    },
                }
            ]
        return self.patch_request("/hosts/{id}", body=payload)

    def get_protected_vm(self, vm_syn_id: str):
        return self.get_request("/vms/{vm_syn_id}", vm_syn_id=vm_syn_id)

    def post_vm_recovery_point(self, vm_syn_id: str, job_id: str):
        return self.post_request("/vms/recovery-points", body={"synId": vm_syn_id, "jobId": job_id})

    def get_recovery_points(self, vm_syn_id: str, limit: int = 100, offset: int = 0):
        return self.get_request(
            "/recovery-points", query_args={"vm_syn_id": vm_syn_id, "limit": limit, "offset": offset}
        )

    def delete_recovery_point(self, recovery_point_id: str):
        return self.delete_request(f"/recovery-points/{recovery_point_id}")

    def post_recovery_point_replicas(self, replicas):
        return self.post_request("/recovery-points/replicas", body=replicas)

    def post_vm_replicas(self, replicas):
        return self.post_request("/vms/replicas", body=replicas)
