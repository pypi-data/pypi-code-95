import logging
from grpc import StatusCode
import grpc
from grpc.aio import ServerInterceptor, AioRpcError
from prometheus_client import (
  Counter,
  Histogram,
  REGISTRY,
  PROCESS_COLLECTOR,
  PLATFORM_COLLECTOR,
)
from prometheus_client.registry import CollectorRegistry
from timeit import default_timer

UNARY = "UNARY"
SERVER_STREAMING = "SERVER_STREAMING"
CLIENT_STREAMING = "CLIENT_STREAMING"
BIDI_STREAMING = "BIDI_STREAMING"
UNKNOWN = "UNKNOWN"

REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(REGISTRY._names_to_collectors["python_gc_objects_collected_total"])


class MetricsInterceptor(ServerInterceptor):
  registry: CollectorRegistry
  delphai_request_count: Counter
  delphai_response_count: Counter
  delphai_latency_seconds: Histogram

  def __init__(self, registry: CollectorRegistry = REGISTRY) -> None:
    self.registry = registry
    self.delphai_request_count = Counter(
      "delphai_request_count",
      "Total number of RPCs started on the server.",
      ["grpc_service", "grpc_method"],
      registry=registry,
    )
    self.delphai_response_count = Counter(
      "delphai_response_count",
      "Total number of RPCs completed on the server, regardless of success or failure.",
      ["grpc_type", "grpc_service", "grpc_method", "grpc_code"],
      registry=registry,
    )
    self.delphai_latency_seconds = Histogram(
      "delphai_latency_seconds",
      "Histogram of response latency (seconds)",
      ["grpc_type", "grpc_service", "grpc_method", "grpc_code"],
      registry=registry,
    )

  def get_method_type(self, request_streaming, response_streaming):
    """
        Infers the method type from if the request or the response is streaming.
        # The Method type is coming from:
        # https://grpc.io/grpc-java/javadoc/io/grpc/MethodDescriptor.MethodType.html
        """
    if request_streaming and response_streaming:
      return BIDI_STREAMING
    elif request_streaming and not response_streaming:
      return CLIENT_STREAMING
    elif not request_streaming and response_streaming:
      return SERVER_STREAMING
    return UNARY

  def split_method_call(self, handler_call_details):
    """
        Infers the grpc service and method name from the handler_call_details.
        """

    # e.g. /package.ServiceName/MethodName
    parts = handler_call_details.method.split("/")
    if len(parts) < 3:
      return "", "", False

    grpc_service_name, grpc_method_name = parts[1:3]
    return grpc_service_name, grpc_method_name, True

  async def _wrap_rpc_behavior(self, handler, fn):
    """Returns a new rpc handler that wraps the given function"""
    if handler is None:
      return None

    if handler.request_streaming and handler.response_streaming:
      behavior_fn = handler.stream_stream
      handler_factory = grpc.stream_stream_rpc_method_handler
    elif handler.request_streaming and not handler.response_streaming:
      behavior_fn = handler.stream_unary
      handler_factory = grpc.stream_unary_rpc_method_handler
    elif not handler.request_streaming and handler.response_streaming:
      behavior_fn = handler.unary_stream
      handler_factory = grpc.unary_stream_rpc_method_handler
    else:
      behavior_fn = handler.unary_unary
      handler_factory = grpc.unary_unary_rpc_method_handler

    return handler_factory(
      await fn(behavior_fn, handler.request_streaming, handler.response_streaming),
      request_deserializer=handler.request_deserializer,
      response_serializer=handler.response_serializer,
    )

  async def intercept_service(self, continuation, handler_call_details):
    grpc_service_name, grpc_method_name, _ = self.split_method_call(handler_call_details)

    async def metrics_wrapper(behavior, request_streaming, response_streaming):
      async def new_behavior(request_or_iterator, servicer_context):
        response_or_iterator = None
        grpc_code = StatusCode.UNKNOWN
        try:
          start = default_timer()
          grpc_type = self.get_method_type(request_streaming, response_streaming)
          try:
            self.delphai_request_count.labels(
              grpc_service=grpc_service_name,
              grpc_method=grpc_method_name,
            ).inc()
            response_or_iterator = await behavior(request_or_iterator, servicer_context)
            grpc_code = StatusCode.OK
            self.delphai_response_count.labels(
              grpc_type=grpc_type,
              grpc_service=grpc_service_name,
              grpc_method=grpc_method_name,
              grpc_code=grpc_code,
            ).inc()
            return response_or_iterator
          except AioRpcError as ex:
            grpc_code = ex.code()
            logging.error(f"[{ex.code()}] {ex.details()}")
            self.delphai_response_count.labels(
              grpc_type=grpc_type,
              grpc_service=grpc_service_name,
              grpc_method=grpc_method_name,
              grpc_code=grpc_code,
            ).inc()
            raise ex
          finally:
            end = default_timer()
            elapsed = end - start
            logging.info(f"[{grpc_code}] {grpc_service_name}/{grpc_method_name} [{round(elapsed * 1000, 2)}ms]")
            self.delphai_latency_seconds.labels(
              grpc_type=grpc_type,
              grpc_service=grpc_service_name,
              grpc_method=grpc_method_name,
              grpc_code=grpc_code,
            ).observe(max(elapsed, 0))
        except Exception as ex:
          return await continuation(handler_call_details)

      return new_behavior

    if grpc_service_name.startswith("grpc"):
      return await continuation(handler_call_details)
    else:
      handler = await continuation(handler_call_details)
      optional_any = await self._wrap_rpc_behavior(handler, metrics_wrapper)
      return optional_any
