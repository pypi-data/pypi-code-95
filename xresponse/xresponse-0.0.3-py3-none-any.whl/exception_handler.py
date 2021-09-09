from rest_framework.views import exception_handler
from .response import XResponse


def xkern_exception_handler(exc, context):
    response = exception_handler(exc, context)

    return XResponse(
        code=response.status_code,
        message=str(exc),
        data=[]
    )
