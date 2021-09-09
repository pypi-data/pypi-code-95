import io

from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from ngs.tools.time import string_to_time
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from ..filters.operation_log import OperationLogFilter
from ..mixins import OperationLogMixin
from ..models import OperationLog
from ..rest.decorator import action_name
from ..rest.viewsets import GenericViewSet
from ..serializers.operation_log import OperationLogSerializer
from ..utils.file_handler import to_csv, to_excel


class OperationLogViewSet(GenericViewSet,
                          ListModelMixin,
                          OperationLogMixin):
    queryset = OperationLog.objects.all().order_by('-create_timestamp')
    serializer_class = OperationLogSerializer
    filter_backends = (SearchFilter, DjangoFilterBackend)
    filter_class = OperationLogFilter
    search_fields = (
        'username',
        'desc',
    )
    known_actions_name = {
        'list': '获取所有操作日志'
    }

    @action_name('导出日志', rest_method='get')
    @action(methods=['post'], detail=False)
    def export_data(self, request):
        file_type = request.data.get('file_type')
        time_range = request.data.get('time_range')
        start_time = int(string_to_time(time_range[0]).timestamp()) * 1000000
        end_time = int(string_to_time(time_range[1]).timestamp()) * 1000000
        result_value = OperationLogSerializer(instance=self.queryset.filter(create_timestamp__gte=start_time,
                                                                            create_timestamp__lte=end_time),
                                              many=True).data
        if not result_value:
            return Response({'msg': '未查询到数据'}, status=400)
        if len(result_value) > 10000:
            return Response({'msg': '数据量过大,请选择合适的时间范围'}, status=400)
        aliases = ['用户名', 'IPV4', '描述', '操作时间']
        field_names = ['username', 'ipv4', 'desc', 'create_timestamp']

        self.operation_log_serializer(**{
            'desc': f'导出操作日志{time_range[0]}到{time_range[1]}数据',
        }).save()

        if file_type == 'csv':
            buffer = to_csv(aliases, field_names, result_value)

            response = FileResponse(buffer, as_attachment=True,
                                    filename=f'history.xlsx')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        elif file_type == 'excel':
            buffer = to_excel(aliases, field_names, result_value)
            response = FileResponse(io.BytesIO(buffer), as_attachment=True,
                                    filename=f'history.xlsx')
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        else:
            return Response(data={'msg': f'不支持的文件格式: {file_type}'}, status=status.HTTP_400_BAD_REQUEST)
