from django.db import transaction
from rest_framework.exceptions import ValidationError

from common.rest_extend.response import Results, RESTResponse, get_error_status_code
from common.rest_extend.views.related import RelatedView


class TagsMToMView(RelatedView):
    def post(
            self,
            request,
            obj,
            obj_serializer,
            *,
            data=None,
            need_results=False,
            raise_exception=False,
            related_objs: list = None,
            m_to_m_objs: list = None,
            related_mapping=None,
            m_to_m_mapping=None,
            key=None,
            tags_obj=None,
            tags_ser=None,
            m_to_m_tags_obj=None,
            m_to_m_tags_obj_ser=None,
            **kwargs,
    ):
        results = Results()
        if not data:
            data = request.data
        if "data" in data and "ops" in data:
            data = data.get("data")

        try:
            with transaction.atomic():
                # if not related_objs:
                #     related_objs, related_mapping = self.injection_data.related_data("POST")
                # if not m_to_m_objs:
                #     m_to_m_objs, m_to_m_mapping = self.injection_data.m_to_m_data("POST")

                response = super().post(
                    request,
                    obj,
                    obj_serializer,
                    data=data,
                    need_results=need_results,
                    raise_exception=True,
                    related_objs=related_objs,
                    m_to_m_objs=m_to_m_objs,
                    related_mapping=related_mapping,
                    m_to_m_mapping=m_to_m_mapping,
                    **kwargs,
                )
                self.update_tags_m_to_m(request, key, data, tags_obj, tags_ser, m_to_m_tags_obj, m_to_m_tags_obj_ser)
                return response
        except Exception as e:
            if raise_exception:
                raise e
            get_error_status_code(e, results)
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
            related_objs: list = None,
            m_to_m_objs: list = None,
            related_mapping=None,
            m_to_m_mapping=None,
            key=None,
            tags_obj=None,
            tags_ser=None,
            m_to_m_tags_obj=None,
            m_to_m_tags_obj_ser=None,
            **kwargs,
    ):
        results = Results()
        try:
            with transaction.atomic():
                if not data:
                    data = request.data
                if "data" in data and "ops" in data:
                    data = data.get("data")
                # if not related_objs:
                #     related_objs, related_mapping = self.injection_data.related_data("PUT")
                # if not m_to_m_objs:
                #     m_to_m_objs, m_to_m_mapping = self.injection_data.m_to_m_data("PUT")
                self.update_tags_m_to_m(request, key, data, tags_obj, tags_ser, m_to_m_tags_obj, m_to_m_tags_obj_ser)

                return super().put(
                    request,
                    obj,
                    obj_serializer,
                    data=data,
                    pk=pk,
                    extend_conditions=extend_conditions,
                    need_results=need_results,
                    need_queryset=need_queryset,
                    raise_exception=True,
                    related_obj=related_objs,
                    m_to_m_obj=m_to_m_objs,
                    related_mapping=related_mapping,
                    m_to_m_mapping=m_to_m_mapping,
                    **kwargs,
                )
        except ValidationError as e:
            if key in str(e):
                results.describe = f"prohibit update unique '{key}'"
            else:
                get_error_status_code(e, results)
        except Exception as e:
            if raise_exception:
                raise e

            get_error_status_code(e, results)
        return RESTResponse(results)

    def update_tags_m_to_m(self, request, key, data, tags_obj, tags_ser, m_to_m_tags_obj, m_to_m_tags_obj_ser):
        if not key or not tags_ser or not tags_obj and m_to_m_tags_obj_ser and m_to_m_tags_obj:
            return

        key_value = data.get(key)
        if not key_value:
            raise ValueError(f"'{key}' can not be empty!!! ")
        instance_list = m_to_m_tags_obj.objects.filter(**{key: key_value}).all()
        cache = set()
        tags_cache = set()
        tags_dict = {}
        for item in instance_list:
            tags_cache.add(item.tags.name)
            tags_dict[item.tags.name] = item
        creator = request._request.tenant.account
        for name in data.get("tags"):
            try:
                if not name:
                    raise ValueError("'tags' can not be empty!!!")
                if name not in cache and name not in tags_cache:

                    tags = tags_obj.objects.filter(name=name).first()
                    if not tags:
                        serializer = tags_ser(data={"name": name, "creator": creator})
                        serializer.is_valid()
                        serializer.save()
                cache.add(name)
                ns_tags_ser = m_to_m_tags_obj_ser(data={key: key_value, "tags": name})
                ns_tags_ser.is_valid(raise_exception=True)
                ns_tags_ser.save()
            except Exception as e:
                if "must make a unique set." in str(e):
                    pass
                else:
                    raise e

        del_cache = tags_cache - cache
        for item in del_cache:
            instance = tags_dict[item]
            instance.delete()
