import os
from .api_client import APIClientBase


class Storage(APIClientBase):
    def __init__(self, url_base=None, **kwargs):
        super().__init__(url_base or os.environ.get("STORAGE_SERVICE", ""), **kwargs)

    def get_pools(self):
        return self.get_request("/pools")

    def get_importable_pools(self):
        return self.get_request("/pools/importable")

    def get_pool(self, pool_name: str):
        return self.get_request("/pools/{pool_name}", pool_name=pool_name)

    def clear_pool(self, pool_name: str):
        return self.put_request("/pools/{pool_name}/clear", pool_name=pool_name)

    def upgrade_pool(self, pool_name: str):
        return self.put_request("/pools/{pool_name}/upgrade", pool_name=pool_name)

    def export_pool(self, pool_name: str):
        return self.put_request("/pools/{pool_name}/export", pool_name=pool_name)

    def get_pool_periodic_scrub(self, pool_name: str):
        return self.get_request("/pools/{pool_name}/scrub/interval", pool_name=pool_name)

    def set_pool_periodic_scrub(self, pool_name: str, interval: str):
        return self.post_request(
            "/pools/{pool_name}/scrub/interval", pool_name=pool_name, query_args={"interval": interval}
        )

    def delete_pool_periodic_scrub(self, pool_name: str):
        return self.delete_request("/pools/{pool_name}/scrub/interval", pool_name=pool_name)

    def start_pool_scrub(self, pool_name: str):
        return self.put_request("/pools/{pool_name}/scrub/start", pool_name=pool_name)

    def stop_pool_scrub(self, pool_name: str):
        return self.put_request("/pools/{pool_name}/scrub/stop", pool_name=pool_name)

    def get_volumes(self, volume_type: str = "NFS", only_clones: bool = False, label_key: str = ""):
        return self.get_request(
            "/volumes", query_args={"volume_type": volume_type, "only_clones": only_clones, "label_key": label_key}
        )

    def create_volume(self, pool_name: str, ips: list, volume_type: str = "NFS", quota: str = "none"):
        hosts = [{"ipNetwork": ip, "accessType": "rw"} for ip in ips]
        body = {
            "type": volume_type,
            "pool": pool_name,
            "nfsShareConfig": {"rootAccess": "true", "hosts": hosts},
            "quota": quota,
        }
        return self.post_request("/volumes", body=body)

    def get_volume(self, volume_id: str):
        return self.get_request("/volumes/{volume_id}", volume_id=volume_id)

    def delete_volume(self, volume_id: str):
        return self.delete_request("/volumes", query_args={"volume_id": volume_id})

    def promote_volume(self, volume_id: str):
        return self.put_request("/volumes/{volume_id}/promote", volume_id=volume_id)

    def get_volume_meta(self, volume_id: str, key: str):
        return self.get_request("/volumes/{volume_id}/meta", volume_id=volume_id, query_args={"key": key})

    def set_volume_meta(self, volume_id: str, key: str, value: dict):
        body = {"key": key, "value": value}
        return self.put_request("/volumes/{volume_id}/meta", volume_id=volume_id, body=body)

    def get_volume_snapshots(self, volume_id: str):
        return self.get_request("/volumes/{volume_id}/snapshots", volume_id=volume_id)

    def create_volume_snapshot(self, volume_id: str, snapshot_name: str):
        return self.post_request(
            "/volumes/{volume_id}/snapshots", volume_id=volume_id, query_args={"snapshot_name": snapshot_name}
        )

    def get_volume_snapshot(self, volume_id: str, snapshot_name: str):
        return self.get_request(
            "/volumes/{volume_id}/snapshots/{snapshot_name}", volume_id=volume_id, snapshot_name=snapshot_name
        )

    def remove_volume_snapshot(self, volume_id: str, snapshot_name: str):
        # Deprecated
        return self.delete_volume_snapshot(volume_id, snapshot_name)

    def delete_volume_snapshot(self, volume_id: str, snapshot_name: str):
        return self.delete_request(
            "/volumes/{volume_id}/snapshots", volume_id=volume_id, query_args={"snapshot_name": snapshot_name}
        )

    def rollback_volume_snapshot(self, volume_id: str, snapshot_name: str):
        return self.put_request(
            "/volumes/{volume_id}/snapshots/{snapshot_name}/rollback", volume_id=volume_id, snapshot_name=snapshot_name
        )

    def get_volume_snapshot_clones(self, volume_id: str, snapshot_name: str):
        return self.get_request(
            "/volumes/{volume_id}/snapshots/{snapshot_name}/clones", volume_id=volume_id, snapshot_name=snapshot_name
        )

    def create_volume_snapshot_clone(self, volume_id: str, snapshot_name: str):
        return self.post_request(
            "/volumes/{volume_id}/snapshots/{snapshot_name}/clones", volume_id=volume_id, snapshot_name=snapshot_name
        )

    def get_volume_files(self, volume_id: str, path: str = "", recursive: bool = False, match_pattern: str = ""):
        return self.get_request(
            "/volumes/{volume_id}/files",
            volume_id=volume_id,
            query_args={"path": path, "recursive": recursive, "match_pattern": match_pattern},
        )

    def delete_volume_files(self, volume_id: str, file_path: str = None, pattern: str = None):
        return self.delete_request(
            "/volumes/{volume_id}/files",
            volume_id=volume_id,
            body={"volume_id": volume_id, "file_path": file_path, "pattern": pattern},
        )

    def get_volume_file_content(self, volume_id: str, file_path: str):
        return self.get_request(
            "/volumes/{volume_id}/files/content", volume_id=volume_id, query_args={"file_path": file_path}
        )

    def set_volume_file_content(self, volume_id: str, file_path: str, content: str):
        return self.post_request(
            "/volumes/{volume_id}/files/content",
            volume_id=volume_id,
            query_args={"file_path": file_path},
            body={"content": content},
        )

    def create_directory_in_volume(self, volume_id: str, dir_path: str):
        return self.post_request("/volumes/{volume_id}/folder", volume_id=volume_id, query_args={"dir_path": dir_path})

    def delete_directory_in_volume(self, volume_id: str, dir_path: str):
        return self.delete_request(
            "/volumes/{volume_id}/folder", volume_id=volume_id, query_args={"dir_path": dir_path}
        )

    def get_file_recovery_volume(self):
        return self.get_request("/file-recovery")

    def create_file_recovery_volume(self, pool_name: str):
        return self.post_request("/file-recovery", body={"pool": pool_name})

    def get_system_information(self):
        return self.get_request("/system")
