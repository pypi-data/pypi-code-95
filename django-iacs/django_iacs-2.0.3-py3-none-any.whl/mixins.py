import json
from typing import Optional, Dict

from .serializers.operation_log import OperationLogSerializer


class OperationLogMixin(object):
    # noinspection PyMethodMayBeStatic,PyUnresolvedReferences
    def operation_log_serializer(self,
                                 desc,
                                 request_data: Optional[Dict] = None,
                                 before: Optional[Dict] = None,
                                 after: Optional[Dict] = None):
        if request_data is not None:
            _request_data = json.dumps(request_data, ensure_ascii=False)
        else:
            _request_data = ''

        if before is not None:
            _before = json.dumps(before, ensure_ascii=False)
        else:
            _before = ''

        if after is not None:
            _after = json.dumps(after, ensure_ascii=False)
        else:
            _after = ''

        serializer = OperationLogSerializer(data={
            'username': self.request.user.username,
            'ipv4': self.get_client_ip(),
            'desc': desc,
            'request_data': _request_data,
            'before': _before,
            'after': _after
        })
        serializer.is_valid(raise_exception=True)
        return serializer

    def save_operation_log(self, desc,
                           request_data: Optional[Dict] = None,
                           before: Optional[Dict] = None,
                           after: Optional[Dict] = None):
        serializer = self.operation_log_serializer(desc, request_data, before, after)
        serializer.save()
