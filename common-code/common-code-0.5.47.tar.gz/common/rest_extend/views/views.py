import abc
import datetime

from common.rest_extend.views.base import Select, BaseORM
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q, Count
from django.db.models.query import QuerySet
from django.http import QueryDict
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from copy import deepcopy
from common.rest_extend.response import (
    Results,
    SUCCESS,
    FAILURE,
    REQUEST_ERROR_CODE,
    SERVER_ERROR_CODE,
    PageTypeResults,
    get_error_status_code,
    RESTResponse,
)
from common.utility.args_parsing import BaseArgsParsing


class ResponseJsonEncoder(DjangoJSONEncoder):
    def default(self, o):
        _o = super(ResponseJsonEncoder, self).default(o)
        if isinstance(o, datetime.datetime):

            return o.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return _o


class BaseView(APIView, Select, BaseORM):
    """
    对实体模型增删改查的父类
    """

    def get(
            self,
            request,
            obj,
            obj_serializer,
            *,
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            keys=None,
            **kwargs,
    ):
        """
        根据键值对查找数据
        :param request:
        :param obj:
        :param obj_serializer:
        :param data:
        :param need_results:
        :param keys:
        :return:
        """

        data = self.get_req_args(request, extend_conditions)
        results, queryset, current_page_queryset = self.find(obj, data, obj_serializer)
        if need_results:
            return results
        if need_queryset:
            return results, queryset
        return RESTResponse(results)

    def post(self, request, obj, obj_serializer, *, data=None, need_results=False, raise_exception=False, **kwargs):
        """
        添加数据

        """
        results = Results()
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        serializer = obj_serializer(data=data)
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            if raise_exception:
                raise e
            results.code, results.describe = get_error_status_code(e)
        else:
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        if need_results:
            return results
        return RESTResponse(results)

    def put(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            raise_exception=False,
            **kwargs,
    ):
        instance = None
        results = Results()
        results.code = 200
        partial = True
        try:
            data, pk, value_pk, conditions = self.parsing_args_and_data(request, results, data, extend_conditions, pk)
            if results.code != 200:
                if need_queryset:
                    return results, None
                if need_results:
                    return results
                return RESTResponse(results)
            orm_q = self.get_orm_q(conditions)
            instance = obj.objects.filter(orm_q).first()
            if not instance:
                results.describe = pk + "=" + str(value_pk) + "  does not exist"
                results.code = REQUEST_ERROR_CODE
            else:
                serializer = obj_serializer(instance, data=data, partial=partial)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    results.describe = "update  successfully！！！"
                    results.status = SUCCESS
                except Exception as e:
                    results.code, results.describe = get_error_status_code(e)
                if getattr(instance, "_prefetched_objects_cache", None):
                    # If 'prefetch_related' has been applied to a queryset, we need to
                    # forcibly invalidate the prefetch cache on the instance.
                    instance._prefetched_objects_cache = {}

        except Exception as e:
            if raise_exception:
                raise e
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        if need_queryset:
            return results, instance
        return RESTResponse(results)

    def delete(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            pk="id",
            extend_conditions: dict = None,
            need_results=False,
            need_queryset=False,
            raise_exception=False,
            **kwargs,
    ):
        instance = None
        results = Results()
        results.code = 200
        try:
            data, pk, value_pk, conditions = self.parsing_args_and_data(request, results, data, extend_conditions, pk)
            if results.code != 200:
                if need_results:
                    return results
                return RESTResponse(results)
            orm_q = self.get_orm_q(conditions)
            instance = obj.objects.filter(orm_q).first()
            if not instance:
                results.describe = pk + "=" + str(value_pk) + " does not exist"
                results.code = REQUEST_ERROR_CODE
            else:
                instance.delete()
                results.describe = "deleted successfully！！！"
                results.status = SUCCESS
        except Exception as e:
            if raise_exception:
                raise e
            results.code, results.describe = get_error_status_code(e)

        if need_results:
            return results
        if need_queryset:
            return results, instance
        return RESTResponse(results)

    def get_queryset(self, obj, data) -> (QuerySet, QuerySet):
        return super(BaseView, self).get_queryset(obj, data)

    def parsing_args_and_data(self, request, results, data, extend_conditions, pk):
        conditions = {}
        if not extend_conditions:
            extend_conditions = {}
        if not data:
            data = request.data
        if data.get("data"):
            data = data.get("data")
        if request.GET.get("pk"):
            pk = request.GET.get("pk")
        value_pk = data.get(pk)
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
        return data, pk, value_pk, conditions
