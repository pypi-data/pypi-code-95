# -*- coding: utf-8 -*-
# @Time: 2020-06-16 12:15:29.561333
import datetime
import os
import time
from collections import OrderedDict
from warnings import filterwarnings

import MySQLdb
from django.db.models import Q
from django.http import HttpResponseRedirect
from drf_yasg.utils import swagger_auto_schema

from ..models.server_connect import ServerConnect
from framework.connections import connections
from framework.filters import MyFilterBackend, MyFilterSerializer, OrderingFilter
from framework.route import Route
from framework.serializer import BaseModelSerializer, EditParams, IdSerializer, IdsSerializer, PaginationSerializer, s
from framework.views import CurdViewSet, HttpResponse, notauth, render, render_to_response
from log_def.models import DictDefine

from framework.settings import settings
from framework.utils import json_dumps, md5, trace_msg, ObjectDict
from addict import Dict
from framework.utils.cache import cache_func, CACHE_TYPE, clear_cache
from .exprot_file import QueryExprot
import logging
from ..models.query import Query, QueryCompiler, SqlMarkManager

filterwarnings('ignore', category=MySQLdb.Warning)


class QuerySerializer(BaseModelSerializer):
    # https://www.django-rest-framework.org/api-guide/serializers/
    # https://www.django-rest-framework.org/api-guide/relations/
    order_type_alias = s.CharField(source='get_order_type_display', required=False, read_only=True)

    class Meta:
        model = Query
        fields = ['id', 'log_key', 'log_type', 'field_config', 'key', 'name', 'select', 'where', 'group', 'order',
                  'order_type', 'sql', 'other_sql', 'cache_validate', 'remark', 'template_name', 'create_datetime',
                  'update_datetime', 'order_type_alias', 'is_paging'] or '__all__'
        # exclude = ['session_key']
        read_only_fields = ['create_datetime', 'update_datetime']
        extra_kwargs = {'password': {'write_only': True}}


class ListQueryRspSerializer(PaginationSerializer):
    results = QuerySerializer(many=True)


@Route('analysis/query')
class QuerySet(CurdViewSet):
    filter_backends = (MyFilterBackend, OrderingFilter)

    serializer_class = QuerySerializer
    # 可条件过滤的字段
    filter_fields = ['id', 'log_key', 'key', 'log_type', 'name', 'select', 'where', 'group', 'order', 'order_type',
                     'sql', 'other_sql', 'cache_validate', 'remark', 'template_name', 'create_datetime',
                     'update_datetime']
    # 可排序的字段
    ordering_fields = ['id', 'log_key', 'key', 'log_type', 'name', 'select', 'where', 'group', 'order', 'order_type',
                       'sql', 'other_sql', 'cache_validate', 'remark', 'template_name', 'create_datetime',
                       'update_datetime']

    model = Query

    def get_queryset(self):
        return Query.objects.all().prefetch_related(*[]).select_related(*[])

    @swagger_auto_schema(query_serializer=MyFilterSerializer, responses=ListQueryRspSerializer)
    def list(self, request, ):
        """查询 列表"""
        return render_to_response('analysis/query/list.html', super().list(request))

    @swagger_auto_schema(query_serializer=EditParams, responses=QuerySerializer)
    def edit(self, request, *args, **kwargs):
        """查询 编辑"""
        data = super().edit(request).data.data
        data.update({'mark_map': SqlMarkManager.mark_map})
        return render_to_response('analysis/query/edit.html', data)

    @swagger_auto_schema(query_serializer=IdSerializer, request_body=QuerySerializer, responses=QuerySerializer)
    def save(self, request, *args, **kwargs):
        """查询 保存"""
        model_instance: Query = self.get_model_instance(IdSerializer)
        model_instance.field_config = request.data.get('field_config', {})
        serializer, msg = self.save_instance(request)
        return self.response(serializer.data, msg=msg)

    @swagger_auto_schema(request_body=IdsSerializer, responses=IdsSerializer)
    def delete(self, request, *args, **kwargs):
        return super(QuerySet, self).delete(request, *args, **kwargs)

    # @swagger_auto_schema(methods=['post'], request_body=QuerySerializer, responses=QuerySerializer)
    # @action(['post'])
    # def foo_action(self, request):
    #     return Response(QuerySerializer().data)


def get_field_id_for_dict(field_dict, value):
    _r = value
    for k, v in field_dict.items():
        if value.strip() == v:
            _r = k
            break
    return str(_r)


@Route('analysis/query/interface/(\S+)$')
@notauth
def interface(request, query_name, template='query_csv'):
    """查询接口
    """
    if not hasattr(request, 'admin'):
        pass

    return query_view(request, query_name=query_name, is_query_do=True)


@Route('analysis/query/widget/(\S+)')
def query_widget(request, query_name):
    return query_view(request, query_name=query_name, is_query_do=False, template='query/query_widget.html')


@Route('query/view$')
@Route('query/view/(\S+)$')
@Route('analysis/query/view$')
@Route('analysis/query/view/(\S+)$')
def query_view(request, query_name='', query_model=None, is_query_do=False, list_data_handle=False,
               template='analysis/query_view.html'):
    """查询视图,request 传入
    @param query_name:查询名称
    @param is_query_do: 是否执行查询
    """

    now = datetime.datetime.now()
    _g = request.REQUEST.get
    _gl = request.REQUEST.getlist

    query_name = query_name or _g('query_name', '') or _g('name', '')
    query_id = int(_g('query_id', '') or _g('qid', '') or 0)

    # 不传id则使用查询名
    if query_id:
        the_query = Query.objects.get(id=query_id)
    elif query_name:
        the_query = Query.objects.using('read').get(Q(name=query_name) | Q(key=query_name))
    elif query_model:
        the_query = query_model

    else:
        return HttpResponse('没有 ID[%s] 或者  [%s] 的查询' % (query_id, query_name))
    params = dict(request.GET)
    params.update(dict(request.POST))  # 必须为POST
    # print params
    params = Dict(params)
    log_def = the_query.log_def
    query_compiler = QueryCompiler(the_query, params)
    is_center_query = the_query.is_center_query
    is_export = _g('is_export', 'False') == 'true'

    if is_export:  # 导出
        return query_export_do(request, query_compiler)
    if is_query_do or request.method == 'POST' or request.REQUEST.get('query_do') or request.GET.get('template', ''):
        return query_do(request, query_compiler, list_data_handle=list_data_handle)

    same_log_key_query_list = Query.objects.filter(
            log_key=the_query.log_key)  # 查询的表定义
    field_configs = OrderedDict()
    conditions_configs = []

    for cloumn in the_query.selects:
        field_config_item = the_query.field_config.get(cloumn, {})
        field_configs[cloumn] = field_config_item

    for k in the_query.field_config.keys():
        field_config_item = the_query.field_config[k]
        if field_config_item.get('single', ''):
            default_value = DictDefine.get_dict_for_key(
                    field_config_item.get('dict', ''))
        else:
            default_value = params.get(
                    field_config_item.get('name', ''), [''])[0]
        field_config_item['value'] = default_value
        field_config_item['request_value'] = params.get(field_config_item.get(
                'name', ''), [''])[0] or field_config_item.get('default_value', '')

        order_num = int(field_config_item.get('order_num', 0) or 99)
        conditions_configs.append((k, field_config_item, order_num))

    conditions_configs.sort(key=lambda x: x[2])

    mark_conditions = query_compiler.generate_mark_conditions()

    sdate = request.REQUEST.get('sdate', '') or (
            now + datetime.timedelta(-6)).strftime('%Y-%m-%d 00:00:00')
    edate = request.REQUEST.get(
            'edate', '') or now.strftime('%Y-%m-%d 23:59:59')

    has_sdate = query_compiler.has_mark('sdate')
    has_edate = query_compiler.has_mark('edate')

    # 如果没有查询区间，默认查询当天的数据
    if mark_conditions['sdate'] and not mark_conditions['edate']:
        sdate = request.REQUEST.get('sdate', '') or now.strftime('%Y-%m-%d 00:00:00')

    has_other_conditions = query_compiler.has_conditions()

    has_conditions = False
    for v in mark_conditions.values():
        if v:
            has_conditions = True
            break

    has_conditions = has_conditions or has_other_conditions

    if request.user.is_agent and not mark_conditions['channel']:
        return render(request, 'framework/block.html', {"err_msg": "'此查询非法!'"})

    plugin_templates = []
    if the_query.template_name:
        for template_name in the_query.template_name.split(','):
            if template_name.strip():
                template_path = 'analysis/plugins/%s.html' % template_name

                plugin_templates.append(
                        template_path)

    server_id = request.REQUEST.get('server_id', 0)

    return render(request, template, locals())


def query_export_do(request, query_compiler: QueryCompiler):
    """查询导出文件
    """

    _g = request.REQUEST.get
    _gl = request.REQUEST.getlist
    export_key = _g('export_key', '')
    is_finish = _g('is_finish', '')  # 完成标记 合并文件
    export_type = int(_g('export_type', '') or 0)
    q_server_id = request.REQUEST.get('server_id', '')
    page_num = int(_g('page_num', '') or 0) or 1  # 页码
    file_type = request.REQUEST.get('file_type', '')
    page_size = 200000
    request.POST.setlist('page_size', [page_size])
    export_fields = _gl('export_fields')

    fields = query_compiler.query.selects
    #  导出字段index
    export_indexs = [fields.index(i) for i in export_fields]

    is_summary = _g('is_summary', '')  # 汇总

    query_exprot = QueryExprot(export_key, export_type)
    if is_finish:  # 完成,文件合并
        merge_file_name = query_exprot.merge_files(fields, export_indexs)
        _r = {"url"       : '/static/export/query/%s' % merge_file_name,
              "export_key": query_exprot.export_key, 'export_type': query_exprot.export_type}
    elif is_summary:  # 文件汇总
        merges = [int(x) for x in request.REQUEST.getlist('merges')]
        done_summary_file_name = query_exprot.summary_file(merges)
        new_url = '/static/export/query/%s' % done_summary_file_name
        return HttpResponseRedirect(new_url)
    else:
        total_record, list_data = query_do(
                request, query_compiler, built_in=True)
        export_file_name = '%s_%s' % (query_compiler.query.name, q_server_id)
        _r = query_exprot.gene_file(
                export_file_name, list_data, fields, export_indexs, page_num, page_size, total_record)
    _r["code"] = 0
    _r["server_id"] = q_server_id
    return HttpResponse(json_dumps(_r))


def query_do(request, query_compiler: QueryCompiler, built_in=False, list_data_handle=None):
    """执行查询
    """

    template_name = request.REQUEST.get('template', '') or 'json'
    now = getattr(request, '_start_time', time.time())
    _g = request.REQUEST.get
    _gl = request.REQUEST.getlist
    err_msg = ''
    server_id = int(request.REQUEST.get('server_id', '0'))

    total_record = total_page = 0
    page_num = int(_g('page_num', '') or 0) or 1  # 页码
    page_size = int(_g('page_size', '') or 0) or 50  # 页数
    session_id = request.REQUEST.get('session_id', '')

    is_ajax = request.is_ajax() or _g('ajax', False)
    list_data = []
    tfoot_data = []
    query_sql = count_sql = ''
    try:
        conn = query_compiler.get_conn(server_id)
        # 设置输入参数
        query_compiler.set_mark_parmas(request)
        # 设置 limit 限制
        query_compiler.set_limit(page_size, page_num)
        # 替换变量，生成 sql
        query_compiler.query_sql_handle()
        fields = query_compiler.query.selects
        # 设置排序
        sort_type = _g('sort_type', '')
        sort_fields_index = int(_g('sort_index', '') or -1)
        if sort_fields_index >= 0 and len(fields) >= sort_fields_index:
            sort_field_name = fields[sort_fields_index]
            sort_key = query_compiler.query.field_config.get(
                    sort_field_name, {}).get('name', '')
            if sort_key and sort_type:
                query_compiler.set_order(sort_key, sort_type)

        count_sql = query_compiler.get_count_sql()
        query_sql = query_compiler.get_query_sql()

        # 知道结果的数量情况下,添加_分页,不执行count设置分页
        if not query_compiler.query.is_paging:
            total_record = page_size

        # 默认不打印sql
        if settings.DEBUG or request.REQUEST.get('_sql', ''):
            print(query_sql)

        cache_time = int(query_compiler.query.cache_validate)
        count_sql_key = md5('%s_%s' % (count_sql, server_id))
        cursor = conn.cursor()
        if not total_record:
            total_record, result_cache_time = cache_func(
                    count_sql_key, get_query_result_cout, (conn, count_sql), timeout=cache_time)

        if total_record:
            query_sql_key = md5('%s_%s' % (query_sql, server_id))
            total_page = total_record / page_size
            if total_record % page_size != 0:
                total_page += 1
            list_data, result_cache_time = cache_func(
                    query_sql_key, get_query_result, (conn, query_sql), timeout=cache_time)
            list_data, result_cache_time = cache_func('display_%s' % query_sql_key, query_display_process, (
                    query_compiler, list_data, page_num, page_size), timeout=cache_time)
            tfoot_sql = query_compiler.get_tfoot_sql()

            if tfoot_sql:
                tfoot_sql_key = md5('%s_%s' % (tfoot_sql, server_id))
                tfoot_data, result_cache_time = cache_func(
                        'tfoot_%s' % tfoot_sql_key, get_query_result, (conn, tfoot_sql), timeout=cache_time)
    except Exception as e:
        err_msg = trace_msg()
        err_msg = '%s\nthe_sql:%s' % (err_msg, query_sql)
        logging.error(err_msg)
    fields = query_compiler.query.selects
    if list_data_handle and callable(list_data_handle):
        list_data = list_data_handle(list_data)
    if built_in:  # 导出
        return (total_record, list_data)

    exec_time = '%.3f' % (time.time() - now)
    response = render(request,
                      'analysis/return/%s.html' % template_name, locals())
    response['Order-Record-Count'] = total_record
    response['Page-Num'] = page_num
    response['Page-Size'] = page_size
    response['Total-Page'] = total_page
    return response


@Route('analysis/query/clear/cache$')
def query_clear_cache(request):
    """清除查询缓存
    """
    clear_cache(CACHE_TYPE.LOG_CACHE)
    return HttpResponse('成功!')
    # return render(request,'feedback.html')


def get_query_result_cout(conn, sql):
    return int(get_query_result(conn, sql)[0][0])


def get_query_result(conn, sql):
    cursor = conn.cursor()
    setattr(cursor, 'use_cache', False)  # 设置一个属性给缓存中间件使用
    cursor.execute(sql)
    _r = cursor.fetchall()
    return _r


ip_db = None

from framework.utils.ip import ip_transform


def query_display_process(query_compiler, list_data, page_num, page_size):
    """值定义处理
    """
    fields = query_compiler.query.selects  # 查询的表头
    field_configs = []
    for field_name in fields:
        field_config = query_compiler.query.field_config.get(field_name, {})
        field_config['field_name'] = field_name
        dict_key = field_config.get('dict', '')
        value_defs = DictDefine.get_dict_for_key(dict_key, reverse=False)
        field_config['value_defs'] = value_defs
        field_configs.append(field_config)
        if field_name == '排名':
            field_config['rank'] = True
    new_list_data = []
    list_data = list(list_data)
    n = (page_num - 1) * page_size if page_num > 1 else 0
    for row in list_data:
        item = list(row)
        item_len = len(item)
        n += 1
        for i, key in enumerate(fields):
            if item_len > i:
                field_config = field_configs[i]
                if field_config.get('rank', False):
                    item[i] = n
                else:
                    item[i] = display_format(field_config, item[i])
            # 如果字段名叫IP归属地， 特殊处理，做一下ip,中文地区转换
            if key == "IP归属地" and item[i]:
                try:
                    item[i] = ip_transform(item[i])
                except:
                    pass

        new_list_data.append(item)

    return new_list_data


def display_format(field_config, value):
    """转格式
    """
    field_name = field_config.get('field_name', '')
    def_values = field_config['value_defs']

    if isinstance(value, (datetime.datetime, datetime.date)):
        if '时间' in field_name:
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        elif '日期' in field_name:
            value = value.strftime('%Y-%m-%d')
        elif '小时' in field_name:
            value = value.strftime('%Y-%m-%d %H')
        else:
            value = value.strftime('%Y-%m-%d %H:%M:%S')
    elif value != None and def_values:
        tmp_value = def_values.get(value,
                                   def_values.get(str(value), value)
                                   )
        if field_config.get('merge_value', False) and value:
            value = '%s(%s)' % (tmp_value, value)
        else:
            value = tmp_value

    return value


@Route()
def template_edit(request):
    return QueryTemplateEdit(request)()


class QueryTemplateEdit(object):
    __static_path = settings.STATIC_ROOT
    __template_dir = settings.TEMPLATE_DIR

    def __init__(self, request):
        self.r = request
        self.edit_type = self.r.REQUEST.get('edit_type', 'query')
        self.template_name = request.REQUEST.get('template_name')
        self.file_path = self.get_path()
        self.action = self.r.REQUEST.get('action')

    def get_path(self):
        return os.path.join(self.__template_dir, 'analysis', 'plugins', '%s.html' % self.template_name)

    def save(self, data):
        with open(self.file_path, 'w') as f:
            f.write(data)

    def __call__(self):
        template_name = self.template_name
        edit_type = self.edit_type
        if self.action == 'save' and self.r.is_post():
            file_content = self.r.REQUEST.get('code', '')
            self.save(file_content)
        elif os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                file_content = f.read()
        else:
            file_content = ''
        return render(self.r, 'analysis/query_template_edit.html', locals())
