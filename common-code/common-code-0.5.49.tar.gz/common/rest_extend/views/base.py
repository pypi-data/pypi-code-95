import abc
from copy import deepcopy
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError
from common.rest_extend.response import (
    PageTypeResults,
    Results,
    get_error_status_code,
    REQUEST_ERROR_CODE,
    RESTResponse,
)
from django.db.models import Q, Count

from common.utility.args_parsing import BaseArgsParsing


class Select(BaseArgsParsing, metaclass=abc.ABCMeta):
    GROUP = "group"

    RESERVED_FIELD = deepcopy(BaseArgsParsing.RESERVED_FIELD) + [GROUP]
    FORBID_VALUES = {GROUP: ["password"]}

    def conver_bool(self, value):
        if isinstance(value, str):
            return value.lower() == "true"
        if isinstance(value, int):
            return value == 1

        if isinstance(value, bool):
            return value
        raise ValueError(f"'value' type cannot be {type(value)}")

    def get_orm_q(self, data):
        """
        获取筛选条件
        :param data:
        :return:
        """
        orm_q = Q()
        for key in data:
            if (not key) or (not data.get(key)):
                continue
            values = data.get(key)
            if key in self.FORBID_VALUES.keys():
                if any(item in values for item in self.FORBID_VALUES[key]):
                    raise ValueError(f" {key}  value cannot be a {values}")

            # 判断预留字段不当查询条件
            if key in self.RESERVED_FIELD:
                continue
            itme = key.split("_")
            if len(itme) > 1:
                real_key = "_".join(itme[:-1])
                keyword = itme[-1].lower()
                if keyword in self.SUFFIX_KEYWORD:
                    if keyword == self.LIKE:
                        orm_q.add(Q(**{real_key + "__contains": data.get(key)}), Q.AND)
                    elif keyword == self.IN:
                        values = data.get(key).split(",")
                        orm_q.add(Q(**{real_key + "__in": values}), Q.AND)
                    elif keyword == self.NOT:
                        orm_q.add(~Q(**{real_key: data.get(key)}), Q.AND)
                    else:
                        orm_q.add(Q(**{real_key + "__" + keyword: values}), Q.AND)
                    continue

            orm_q.add(Q(**{key: data.get(key)}), Q.AND)

        return orm_q

    def get_page_type_results(self, result, total, page, size, *args, **kwargs):
        """
        获取当前页面结果集
        :param result:
        :param total:
        :param page:
        :param size:
        :param args:
        :param kwargs:
        :return:
        """
        page_type_results = PageTypeResults()
        # page_type_results.group = group_result
        page_type_results.result = result
        page_type_results.total = total
        page_type_results.page = page
        page_type_results.size = size
        return page_type_results

    def paging(self, queryset, data, obj_serializer=None):
        """
        分页
        :param queryset:
        :param data:
        :return:
        """
        total = len(queryset)
        all_result = self.conver_bool(data.get(self.ALL_RESULT, False))
        if not all_result:
            page, size = self.get_page_and_size(data)
        else:
            page = 1
            size = len(queryset)

        start = (page - 1) * size
        end = page * size
        current_page_queryset = queryset[start:end]
        current_page_result = []
        if current_page_queryset:
            # 如果是group  queryset是dict类型
            if not isinstance(current_page_queryset[0], dict):
                if obj_serializer:
                    current_page_result = list(obj_serializer(current_page_queryset, many=True).data)
                else:
                    current_page_result = list(queryset.values()[start:end])
            else:
                current_page_result = current_page_queryset
        return current_page_queryset, current_page_result, total, page, size

    def select(self, obj, data):
        """
        执行查询
        :param obj:
        :param data:
        :return:
        """
        orm_q = self.get_orm_q(data)
        queryset = obj.objects.select_related().filter(orm_q).all()
        return queryset

    def sort_queryset(self, data, queryset):
        """
        排序
        :param data:
        :param queryset:
        :return:
        """
        field, sort = self.get_sort(data, default_field="id", default_sort=self.DESC)
        queryset = queryset.order_by(field if Select.ASC == sort else f"-{field}")

        return queryset

    def group(self, obj, data):
        """
        group
        :param obj:
        :param data:
        :return:
        """
        orm_q = self.get_orm_q(data)
        group = data.get(self.GROUP)
        if group:
            group = tuple(group.split(","))
            queryset = obj.objects.select_related().filter(orm_q).all()
            queryset = queryset.values(*group).annotate(count=Count("id"))
        else:
            raise Exception(f"'{self.GROUP}'  is None!!!")
        return queryset

    def find(self, obj, data, obj_serializer=None):
        """
        查询、并返回Results
        1、获取queryset
        2、排序
        3、分页
        4、获取当前页结果
        5、扩展当前页结果
        :param obj:
        :param data:
        :return:
        """
        results = Results()
        queryset = None
        current_page_queryset = None
        try:
            # 获取queryset ；extend_queryset用于扩展页面数据集
            queryset, extend_queryset = self.get_queryset(obj, data)
            queryset = self.sort_queryset(data, queryset)
            current_page_queryset, current_page_result, total, page, size = self.paging(queryset, data, obj_serializer)
            page_type_results = self.get_page_type_results(current_page_result, total, page, size)
            self.extend_page_type_results(data, page_type_results, extend_queryset)
            results.data = page_type_results
            results.data_length = len(page_type_results.result)
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)
        return results, queryset, current_page_queryset

    @abc.abstractmethod
    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        group = data.get(self.GROUP)
        if group:
            queryset = self.group(obj, data)
        else:
            queryset = self.select(obj, data)
        return queryset, None

    def extend_page_type_results(self, data, page_type_results, extend_queryset, *args, **kwargs):
        pass


class BaseORM:
    def get_data(self, request, data):
        if not data:
            data = request.data
            if isinstance(data, dict):
                if "ops" in data.keys() and "data" in data.keys():
                    data = data.get("data")
        return data

    def get_req_args(self, request, extend_conditions):
        data = request.GET.dict()
        if extend_conditions:
            data = {**data, **extend_conditions}
        return data

    def parsing_args_and_data(self, request, results, data, extend_conditions=None, pk="id") -> (dict, dict, str, any):
        conditions = {}
        req_args = self.get_req_args(request, extend_conditions)
        data = self.get_data(request, data)
        value_pk = req_args.pop(pk, None)
        if not value_pk:
            results.describe = "'pk' cannot be empty"
            results.code = REQUEST_ERROR_CODE
        else:
            try:
                if pk == "id":
                    try:
                        value_pk = int(value_pk)
                    except:
                        raise ValidationError("'pk' type error Should be <int>！！！")
                conditions = dict(**{pk: value_pk}, **extend_conditions)
            except Exception as e:
                results.code, results.describe = get_error_status_code(e)
        return conditions, data, pk, value_pk

    def execute(self):
        pass

    def get_results(self, results, queryset=None, need_results=False, need_queryset=False) -> any:
        if need_results:
            return results
        if need_queryset:
            if queryset is None:
                raise Exception("'need_queryset' is True but 'queryset' is None!!!")
            return results, queryset
        return RESTResponse(results)
