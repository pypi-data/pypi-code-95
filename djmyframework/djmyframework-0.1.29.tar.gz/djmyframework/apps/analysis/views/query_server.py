# -*- coding: utf-8 -*-
# @Time: 2021-09-10 14:28:17.956883


from drf_yasg.utils import swagger_auto_schema
from framework.filters import MyFilterBackend, OrderingFilter, MyFilterSerializer
from framework.translation import _
from framework.route import Route
from framework.serializer import s, BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, ParamsSerializer, \
    PaginationSerializer
from framework.views import CurdViewSet, ListPageNumberPagination, Response, action, Request, RspError
from framework.views import render_to_response as rt
from analysis.models import QueryServer


class QueryServerSerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    status_alias = s.CharField(source='get_status_display', required=False, read_only=True)

    class Meta:
        model = QueryServer
        fields = ['id', 'name', 'alias', 'host', 'user', 'password', 'port', 'db_name', 'charset', 'status', 'remark',
                  'order', 'create_datetime', 'update_datetime', 'status_alias'] or '__all__'
        # exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        # extra_kwargs = {'password': {'write_only': True}}


class ListQueryServerRspSerializer(PaginationSerializer):
    results = QueryServerSerializer(many=True)


@Route('analysis/query_server')
class QueryServerSet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)

    serializer_class = QueryServerSerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'name', 'alias', 'host', 'user', 'password', 'port', 'db_name', 'charset', 'status',
                     'remark', 'order', 'create_datetime', 'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'name', 'alias', 'host', 'user', 'password', 'port', 'db_name', 'charset', 'status',
                       'remark', 'order', 'create_datetime', 'update_datetime']
    # 可以查询字段
    queryset_fields = ['id', 'name', 'alias', 'host', 'user', 'password', 'port', 'db_name', 'charset', 'status',
                       'remark', 'order', 'create_datetime', 'update_datetime']

    model = QueryServer

    def get_queryset(self):
        return QueryServer.objects.all().prefetch_related(*[]).select_related(*[]).only(*QueryServerSet.queryset_fields)

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListQueryServerRspSerializer)
    def list(self, request):
        """查询服务器 列表"""
        return rt("analysis/query_server/list.html", super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=QueryServerSerializer)
    def edit(self, request):
        """查询服务器 编辑"""
        return rt("analysis/query_server/edit.html", super().edit(request))

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=QueryServerSerializer,
                         responses=QueryServerSerializer)
    def save(self, request):
        """查询服务器 保存"""
        return super().save(request)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request):
        """查询服务器 删除"""
        return super().delete(request)

    @swagger_auto_schema(methods=['post'], request_body=QueryServerSerializer, responses=QueryServerSerializer)
    @action(['post'])
    def test_connect(self, request):
        params = QueryServerSerializer(data=request.data, valid_exception=True).o
        errmsg, model = QueryServer.create_or_update_for_params(params)
        connect_name = model.alias or model.name
        conn = model.mysql_conn()
        if not conn:
            raise RspError(_(' %s 获取 Mysql 连接失败 %s') % (connect_name, errmsg))
            cur = conn.cursor()
            cur.execute("SELECT 1")

        return Response(msg=_('%s 连接成功') % connect_name)
