import os
from .api_client import APIClientBase, APIException


class Virtualization(APIClientBase):
    def __init__(self, url_base=None, **kwargs):
        super().__init__(url_base or os.environ.get("VIRTUALIZATION_SERVICE", ""), **kwargs)

        # Deprecated methods, please don't use them
        self.get_vm_by_syn_id = self.get_virtual_machine

    def get_hypervisors(self):
        return self.get_request("/hypervisors")

    def get_hypervisor(self, hypervisor_id: str):
        return self.get_request("/hypervisors/{uuid}", uuid=hypervisor_id)

    def get_vms(self):
        return self.get_request("/vms")

    def get_virtual_machine(self, vm_syn_id: str):
        return self.get_request("/vms/{vm_syn_id}", vm_syn_id=vm_syn_id)

    def edit_vm(self, vm_syn_id: str, body: dict):
        return self.patch_request("/vms/{vm_syn_id}", vm_syn_id=vm_syn_id, body=body)

    def get_vmware_hosts(self):
        return self.get_request("/vmware/hosts")

    def get_vmware_datastores(self):
        return self.get_request("/vmware/datastores")

    def get_vm_snapshot(self, vm_syn_id: str, snapshot_name: str):
        snapshots = self.get_request("/vmware/vms/{vm_syn_id}/snapshots", vm_syn_id=vm_syn_id)
        return next((snap for snap in snapshots if snap["name"] == snapshot_name), None)

    def create_vm_snapshot(
        self, vm_syn_id: str, snapshot_name: str, quiesce: bool = True, dumpmem: bool = False,
    ):
        body = {
            "vmSynId": vm_syn_id,
            "snapshotName": snapshot_name,
            "description": snapshot_name,
            "quiesce": quiesce,
            "dumpmem": dumpmem,
        }
        return self.post_request(
            "/vmware/vms/{vm_syn_id}/snapshots", vm_syn_id=vm_syn_id, query_args={"in_background": "False"}, body=body,
        )

    def delete_vm_snapshot(self, vm_syn_id, snapshot_ref_id, consolidate=True, remove_children=True):
        body = {
            "vmSynId": vm_syn_id,
            "snapshotRefId": snapshot_ref_id,
            "consolidate": consolidate,
            "removeChildren": remove_children,
        }
        self.delete_request(
            "/vmware/vms/{vm_syn_id}/snapshots",
            vm_syn_id=vm_syn_id,
            query_args={"in_background": "False"},
            body=body,
            success_codes=[200, 202, 204],
        )

    def create_nas_datastore(self, server: str, mountpoint: str, hosts_syn_ids=None, datastore_name=None):
        return self.post_request(
            "/vmware/datastores",
            body={
                "server": server,
                "name": datastore_name,
                "mountpoint": mountpoint,
                "hosts_syn_ids": hosts_syn_ids if hosts_syn_ids else [],
                "name": datastore_name,
            },
        )

    def delete_nas_datastore(self, syn_id: str = None, mountpoint: str = None):
        return self.delete_request(
            "/vmware/datastores",
            query_args={"datastore_syn_id": syn_id if syn_id else "", "datastore_mountpoint": mountpoint},
        )
