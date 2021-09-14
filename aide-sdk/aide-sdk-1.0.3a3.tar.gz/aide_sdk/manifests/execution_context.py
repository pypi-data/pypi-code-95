import dataclasses
import threading
import uuid

from aide_sdk.manifests.manifest import load, set_manifest

execution_data = threading.local()


def get_execution_context(manifest=None):
    if not hasattr(execution_data, 'global_context'):
        start_new_execution(manifest)
    return execution_data.global_context


def start_new_execution(manifest=None):
    if manifest:
        # Set the manifest to be the new global manifest
        set_manifest(manifest)

    manifest = load()

    execution_data.global_context = ExecutionContext(execution_uid=uuid.uuid4(),
                                                     model_name=manifest.model_name,
                                                     model_version=manifest.model_version,
                                                     model_uid=manifest.model_uid,
                                                     mode=manifest.mode)
    return execution_data.global_context


@dataclasses.dataclass
class ExecutionContext:
    execution_uid: uuid.UUID
    model_uid: str
    model_name: str = None
    model_version: str = None
    mode: str = None
    clinical_review_received: bool = None
    status: str = 'success'
    message: str = None
