from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from google.auth import transport
import time
import google.cloud.logging
import os
import random
import google.auth
import google.oauth2.id_token

client = google.cloud.logging.Client()
SERVICE = os.getenv('SERVICE')
logger = client.logger(SERVICE)
_, PROJECT_ID = google.auth.default()

from starlette_context.plugins import Plugin
from starlette_context import context


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
    id_token = id_token=generate_token(service_url)
    headers = {
        u'Authorization': u'Bearer {}'.format(id_token),
        u'X-Cloud-Trace-Context': u'{}'.format(logging.get_trace_context())
    }

    return (headers, id_token)


class TracePlugin(Plugin):
    key = "x-cloud-trace-context"

class LogMidddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
       
        request.state.trace = logging.get_trace()
        host = request.client.host
        logger.log_struct({"message": f"request stated by {host} to service {SERVICE}"}, 
                        trace=request.state.trace,
                        severity="INFO",
                        http_request={
                                        "requestMethod": request.method,
                                        "requestUrl": request.url._url,
                                        "userAgent": request.headers.get('user-agent')
                                        }
                            )
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time)
        formatted_process_time = '{0:.2f}'.format(process_time)

        domain='unknown'
        user='unknown'
        if hasattr(request.state, 'current_user'):
            domain = request.state.current_user.get('domain', 'unknown')
            user = request.state.current_user.get('_id', 'unknown')

        logger.log_struct({"message": f"request completed_in={formatted_process_time}ms status_code={response.status_code} at service {SERVICE}"}, 
                        trace=request.state.trace,
                        severity="INFO",
                        http_request={
                                        "latency": f"{formatted_process_time}s",
                                        "protocol": request.scope.get('type').upper() + '/' + request.scope.get('http_version'),
                                        "responseSize":  response.headers.get('content-length'),
                                        "requestMethod": request.method,
                                        "requestUrl": request.url._url,
                                        "userAgent": request.headers.get('user-agent'),
                                        "status": response.status_code
                                        },
                        labels={
                                'domain' : domain,
                                'service_account' : user,
                        }
                        ),
        
        return response

class logging():
    @staticmethod
    def get_trace() -> str:
        trace = context.get('x-cloud-trace-context')
        if trace:
            trace_id = trace.split('/')[0]
            return f"projects/{PROJECT_ID}/traces/{trace_id}"
        
        return f"projects/{PROJECT_ID}/traces/{context.get('X-Request-ID')}"
    
    @staticmethod
    def get_trace_context() -> str:
        trace = context.get('x-cloud-trace-context')
        if trace:
            return trace

        span_id = random.randint(1000000000000000000, 9999999999999999999)
        return f"{context.get('X-Request-ID')}/{span_id};o=1"
    
    @staticmethod
    def get_auth_token(service_url: str) -> str:
        return generate_token(service_url)

    @staticmethod
    def get_auth_header(service_url:str) -> dict:
        return get_default_headers(service_url)

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


            

