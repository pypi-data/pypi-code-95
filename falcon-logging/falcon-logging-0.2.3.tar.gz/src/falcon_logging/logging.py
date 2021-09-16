from google.auth import transport
import google.cloud.logging
import google.auth
import threading
import time, os, random
import google.oauth2.id_token

from uuid import uuid4
from falcon import Request, Response


SERVICE = os.getenv('SERVICE')
_, PROJECT_ID = google.auth.default()

client = google.cloud.logging.Client()
logger = client.logger(SERVICE)


def generate_token(service_url) -> str:
    """
    Genarate id token for authentication service to service using container Service account
    """
    auth_req = transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, service_url)

    return id_token


def get_default_headers(service_url):
    """
    Generate Dictionary header with Authentication param and X-Cloud-Trace-Context param
    for continuous tracing
    """
    return {
        u'Authorization': u'Bearer {id_token}'.format(id_token=generate_token(service_url)),
        u'X-Cloud-Trace-Context': u'{}'.format(logging.get_trace_context()),
    }


class _Context:
    def __init__(self):
        self._thread_local = threading.local()

    @property
    def request_id(self):
        return getattr(self._thread_local, 'request_id', None)
    
    @property
    def trace(self):
        return getattr(self._thread_local, 'trace', None)
    
    @property
    def trace_context(self):
        return getattr(self._thread_local, 'trace_context', None)

    @property
    def endpoint_api_userinfo(self):
        return getattr(self._thread_local, 'endpoint_api_userinfo', None)

    @request_id.setter
    def request_id(self, value):
        self._thread_local.request_id = value

    @trace.setter
    def trace(self, value):
        self._thread_local.trace = value

    @trace_context.setter
    def trace_context(self, value):
        self._thread_local.trace_context = value
    
    @endpoint_api_userinfo.setter
    def trace_context(self, value):
        self._thread_local.endpoint_api_userinfo = value


ctx = _Context


def set_request_id(request: Request, response: Response):
    cloud_trace_context = request.get_header('X-CLOUD-TRACE-CONTEXT', None)

    if not cloud_trace_context:
        ctx.request_id = str(uuid4())
        
        cloud_trace_context = \
            f'{ctx.request_id}/{str(random.randint(1000000000000000000, 9999999999999999999))};o=1'
    else:
        ctx.request_id = cloud_trace_context.split('/')[0]
    
    ctx.trace = f"projects/{PROJECT_ID}/traces/{ctx.request_id}"
    ctx.trace_context = cloud_trace_context

    ctx.endpoint_api_userinfo = request.get_header('X-ENDPOINT-API-USERINFO', None)
    
    request.context.cloud_trace_context = cloud_trace_context
    request.context.trace = ctx.trace

    response.set_header('X-CLOUD-TRACE-CONTEXT', cloud_trace_context)


    return


class LogMiddleware(object):

    def process_request(self, request:Request, response:Response):

        set_request_id(request, response)

        host = request.host

        logger.log_struct({"message": f"request stated by {host} to service {SERVICE if SERVICE else 'unknown'}"},
            trace=request.context.trace,
            severity="INFO",
            http_request={
                "requestMethod": request.method,
                "requestUrl": request.url,
                "userAgent": request.headers.get('user-agent')
            })

        request.context.start_time = time.time()

    def process_response(self, request: Request, response: Response, resource, request_succeeded):

        process_time = (time.time() - request.context.start_time)

        formatted_process_time = '{0:.2f}'.format(process_time)

        domain = request.context.domain if hasattr(request.context, 'domain') else 'undefined'
        user = request.context.account if hasattr(request.context, 'account') else 'undefined'

        logger.log_struct(
            {"message": f"rid=1 completed_in={formatted_process_time}ms status_code={int(response.status[:3])}"}, 
            trace=request.context.trace,
            severity="INFO",
            http_request={
                "latency": f"{formatted_process_time}s",
                "protocol": request.scheme.upper(),
                "responseSize":  response.headers.get('content-length'),
                "requestMethod": request.method,
                "requestUrl": request.url,
                "userAgent": request.headers.get('user-agent'),
                "status": int(response.status[:3])
            },
            labels={
                'domain': domain,
                'service_account': user,
            })

class logging():
    @staticmethod
    def get_trace() -> str:
        if ctx.trace:
            return ctx.trace

        ctx.request_id = str(uuid4())
        ctx.trace = f"projects/{PROJECT_ID}/traces/{ctx.request_id}"
        ctx.trace_context = f'{ctx.request_id}/{str(random.randint(1000000000000000000, 9999999999999999999))};o=1'

        return ctx.trace
    
    @staticmethod
    def get_trace_context() -> str:
        return ctx.trace_context
    
    @staticmethod
    def get_auth_token(service_url: str) -> str:
        return generate_token(service_url)

    @staticmethod
    def get_auth_header(service_url:str) -> dict:
        return (get_default_headers(service_url), ctx.endpoint_api_userinfo)

    @staticmethod
    def info(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="INFO")

    @staticmethod
    def warning(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="WARNING")

    @staticmethod
    def error(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="ERROR")

    @staticmethod
    def critical(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="CRITICAL")

    @staticmethod
    def alert(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="ALERT")

    @staticmethod
    def emergency(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="EMERGENCY")

    @staticmethod
    def debug(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="DEBUG")

    @staticmethod
    def default(message: dict):
        logger.log_struct(message, trace=logging.get_trace(), severity="DEFAULT")

