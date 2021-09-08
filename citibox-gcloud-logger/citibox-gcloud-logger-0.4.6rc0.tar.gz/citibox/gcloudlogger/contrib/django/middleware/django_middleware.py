from citibox.gcloudlogger.contrib import Middleware
from citibox.gcloudlogger.contrib.django.django_record_factory import DjangoRecordFactory


class DjangoMiddleware(Middleware):

    def __init__(self, get_response):
        super().__init__()
        self._get_response = get_response
        self.request = None
        self.logRecord = None
        self.view_kwargs = {}

    def __call__(self, request):
        created_at = DjangoRecordFactory.get_current_timestamp()
        request_body = request.body
        response = self._get_response(request)

        log_record_factory = DjangoRecordFactory(
            created_at=created_at,
            logger=self.logger,
            response=response,
            request=request,
            request_body=request_body,
            view_kwargs=self.view_kwargs
        )

        try:
            log_record = log_record_factory.build()

            self.logger.info(
                f'{request.method} {response.status_code} {request.path}',
                extra=log_record.to_dict()
            )
        except Exception:  # pragma: no cover
            pass

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.view_kwargs = view_kwargs
