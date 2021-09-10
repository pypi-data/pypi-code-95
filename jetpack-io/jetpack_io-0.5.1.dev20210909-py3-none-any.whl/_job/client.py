import os
from enum import Enum, auto, unique
from typing import Callable

import grpc
from jetpack._remote import codec
from jetpack.config import namespace, symbols
from jetpack.proto.runtime.v1alpha1 import remote_pb2, remote_pb2_grpc


# assigns human-readable values, as in: LaunchJobMode.FIRE_AND_FORGET = 'FIRE_AND_FORGET'
# https://docs.python.org/3/library/enum.html#using-automatic-values
class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


@unique
class LaunchJobMode(AutoName):
    ASYNC = auto()
    ASYNC_FIRE_AND_FORGET = auto()
    FIRE_AND_FORGET = auto()
    BLOCKING = auto()

    def is_async(self):
        return self == self.ASYNC or self == self.ASYNC_FIRE_AND_FORGET

    def is_fire_and_forget(self):
        return self == self.FIRE_AND_FORGET or self == self.ASYNC_FIRE_AND_FORGET

    # Named this is_wait_for_response instead of is_blocking because the latter
    # sounds confusing with async. Maybe we should rename BLOCKING to REGULAR?
    def is_wait_for_response(self):
        return self == self.ASYNC or self == self.BLOCKING


class JetpackException(Exception):
    """Base class for exceptions in this module"""

    pass


class RuntimeException(JetpackException):
    """Exception raised for errors in the Jetpack runtime and kubernetes."""

    def __init__(self, message):
        self.message = message


class ApplicationException(JetpackException):
    """Exception raised for errors from application-code that is using the SDK.

    TODO DEV-157
    For exceptions raised by remote functions and jobs, we serialize the
    userland exception in the backend and save it here. The userland exception
    is re-raised by the SDK for the caller of the remote function or job.
    """

    def __init__(self, message):
        self.message = message


class NoControllerAddressError(JetpackException):
    pass


class Client:
    def __init__(self):
        host = os.environ.get(
            "JETPACK_CONTROLLER_HOST",
            "remotesvc.jetpack-runtime.svc.cluster.local",
        )
        port = os.environ.get("JETPACK_CONTROLLER_PORT", "443")
        self.address = f"{host}:{port}"
        self.stub = None
        self.async_stub = None
        self.is_dialed = False  # TODO: Mutex needed?
        self.dry_run = False
        self.dry_run_last_request = None

    def dial(self):
        if not self.address:
            raise NoControllerAddressError("Controller address is not set")
        # Since this is inter-cluster communication, insecure is fine.
        # In the future this won't even leave the pod, and use a sidecar so
        # it will be localhost.

        # TODO(Landau): When/how should we close the channels?
        channel = grpc.insecure_channel(self.address)
        self.stub = remote_pb2_grpc.RemoteExecutorStub(channel)
        async_channel = grpc.aio.insecure_channel(self.address)
        self.async_stub = remote_pb2_grpc.RemoteExecutorStub(async_channel)

        self.is_dialed = True

    def launch_job(self, qualified_name: str, module_id: str, args=None, kwargs=None):
        """Launches a k8s job and blocks until the job completes, before returning.
        For now this function assumes job will live in same namespace where the
        launcher is located.

        Keyword arguments:
        qualified_name -- qualified name as produced by utils.qualified_func_name
        module -- jetpack module where the job resides. Used to determine correct
        docker image.
        """
        response = self._launch_job(
            LaunchJobMode.BLOCKING, qualified_name, module_id, args, kwargs
        )

        return self._transform_response_exception(response)

    async def launch_async_job(
        self, qualified_name: str, module_id: str, args=None, kwargs=None
    ):
        response = await self._launch_job(
            LaunchJobMode.ASYNC, qualified_name, module_id, args, kwargs
        )

        return self._transform_response_exception(response)

    def launch_fire_and_forget_job(
        self, qualified_name: str, module_id: str, args=None, kwargs=None
    ):
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

    async def launch_fire_and_forget_async_job(
        self, qualified_name: str, module_id: str, args=None, kwargs=None
    ):
        return await self._launch_job(
            LaunchJobMode.ASYNC_FIRE_AND_FORGET, qualified_name, module_id, args, kwargs
        )

    def _build_request(
        self, mode: LaunchJobMode, qualified_name: str, module_id: str, args, kwargs
    ):
        encoded_args = None
        if args or kwargs:
            encoded_args = codec.encode_args(
                args if args else None,
                kwargs if kwargs else None,
            ).encode("utf-8")

        job = remote_pb2.RemoteJob(
            container_image=symbols.find_image_for_module(module_id),
            qualified_symbol=qualified_name,
            namespace=namespace.get(),
            encoded_args=encoded_args,
            module_id=module_id,
        )
        request = None

        if mode.is_fire_and_forget():
            request = remote_pb2.LaunchJobRequest(job=job)
        elif mode.is_wait_for_response():
            request = remote_pb2.LaunchBlockingJobRequest(job=job)
        else:
            raise Exception(f"unsupported mode: {mode}")

        if self.dry_run:
            self.dry_run_last_request = request

        return request

    def _launch_job(
        self, mode: LaunchJobMode, qualified_name: str, module_id: str, args, kwargs
    ):
        request = self._build_request(mode, qualified_name, module_id, args, kwargs)

        # TODO(Landau): This is gross, remove dry_run.
        if self.dry_run:
            if mode.is_async():

                async def empty_awaitable():
                    pass

                return empty_awaitable()
            return

        # If dialing is slow, consider dialing earlier.
        if not self.is_dialed:
            self.dial()

        if mode == LaunchJobMode.FIRE_AND_FORGET:
            return self.stub.LaunchJob(request)
        elif mode == LaunchJobMode.BLOCKING:
            return self.stub.LaunchBlockingJob(request)

        # Async flavors return a coroutine.
        elif mode == LaunchJobMode.ASYNC:
            return self.async_stub.LaunchBlockingJob(request)
        elif mode == LaunchJobMode.ASYNC_FIRE_AND_FORGET:
            return self.async_stub.LaunchJob(request)
        else:
            raise Exception(f"unsupported mode: {mode}")

    def _transform_response_exception(self, response):
        if not isinstance(response, remote_pb2.LaunchBlockingJobResponse):
            # can happen for dry-run
            # TODO this is a code-smell. We should instead properly mock
            # the response from the grpc call.
            return

        if (
            response.result.error is None
            or response.result.error.code == remote_pb2.ErrorCode.UNKNOWN
        ):
            return response.result.value
        else:
            if response.result.error.code == remote_pb2.ErrorCode.APPLICATION:
                raise ApplicationException(response.result.error.message)
            else:
                raise RuntimeException(response.result.error.message)
