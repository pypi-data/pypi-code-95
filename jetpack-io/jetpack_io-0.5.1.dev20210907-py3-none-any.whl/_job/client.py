import os
from enum import Enum, auto, unique
from typing import Callable

import grpc
from jetpack._remote import codec
from jetpack.config import namespace, symbols
from jetpack.proto import remote_api_pb2, remote_api_pb2_grpc


# assigns human-readable values, as in: LaunchJobMode.FIRE_AND_FORGET = 'FIRE_AND_FORGET'
# https://docs.python.org/3/library/enum.html#using-automatic-values
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class LaunchJobMode(AutoName):
    FIRE_AND_FORGET = auto()
    BLOCKING = auto()


class NoControllerAddressError(Exception):
    pass


class Client:
    def __init__(self):
        host = os.environ.get(
            "JETPACK_CONTROLLER_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_CONTROLLER_PORT", "443")
        self.address = f"{host}:{port}"
        self.channel = None
        self.stub = None
        self.is_dialed = False  # TODO: Mutex needed?
        self.dry_run = False
        self.dry_run_last_request = None

    def dial(self):
        if not self.address:
            raise NoControllerAddressError("Controller address is not set")
        # Since this is inter-cluster communication, insecure is fine.
        # In the future this won't even leave the pod, and use a sidecar so
        # it will be localhost.
        self.channel = grpc.insecure_channel(self.address)
        self.stub = remote_api_pb2_grpc.RemoteExecutorStub(self.channel)
        self.is_dialed = True

    def launch_job(self, qualified_name: str, module_id: str, args=None, kwargs=None):
        """Launches a k8s job. For now this function assumes job will live in
        same namespace where the launcher is located.

        Keyword arguments:
        qualified_name -- qualified name as produced by utils.qualified_func_name
        module -- jetpack module where the job resides. Used to determine correct
        docker image.
        """
        return self._launch_job(
            LaunchJobMode.FIRE_AND_FORGET, qualified_name, module_id, args, kwargs
        )

    def launch_blocking_job(
        self, qualified_name: str, module_id: str, args=None, kwargs=None
    ):
        """Launches a k8s job and blocks until the job completes, before returning.
        For now this function assumes job will live in same namespace where the
        launcher is located.

        Keyword arguments:
        qualified_name -- qualified name as produced by utils.qualified_func_name
        module -- jetpack module where the job resides. Used to determine correct
        docker image.
        """
        return self._launch_job(
            LaunchJobMode.BLOCKING, qualified_name, module_id, args, kwargs
        )

    def _launch_job(
        self, mode: LaunchJobMode, qualified_name: str, module_id: str, args, kwargs
    ):
        encoded_args = None
        if args or kwargs:
            encoded_args = codec.encode_args(
                args if args else None,
                kwargs if kwargs else None,
            ).encode("utf-8")

        job = remote_api_pb2.RemoteJob(
            container_image=symbols.find_image_for_module(module_id),
            qualified_symbol=qualified_name,
            namespace=namespace.get(),
            encoded_args=encoded_args,
            module_id=module_id,
        )
        request = None
        if mode == LaunchJobMode.FIRE_AND_FORGET:
            request = remote_api_pb2.LaunchJobRequest(job=job)
        elif mode == LaunchJobMode.BLOCKING:
            request = remote_api_pb2.LaunchBlockingJobRequest(job=job)
        else:
            raise Exception(f"unsupported mode: {mode}")

        if self.dry_run:
            self.dry_run_last_request = request
            print(f"Dry Run (mode = {mode}):\n{request}")
            return

        # If dialing is slow, consider dialing earlier.
        if not self.is_dialed:
            self.dial()

        if mode == LaunchJobMode.FIRE_AND_FORGET:
            return self.stub.LaunchJob(request)
        elif mode == LaunchJobMode.BLOCKING:
            return self.stub.LaunchBlockingJob(request)
        else:
            raise Exception(f"unsupported mode: {mode}")
