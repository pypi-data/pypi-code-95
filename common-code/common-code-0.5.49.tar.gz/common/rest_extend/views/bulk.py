from rest_framework.views import APIView
from common.rest_extend.response import get_error_status_code, Results
from common.rest_extend.views.base import BaseORM



class BulkView(BaseORM, APIView):

    def post(self, request, obj, obj_serializer, *, data=None, need_results=False, **kwargs):
        results = Results()
        try:
            data = self.get_data(request, data)
            if not isinstance(data, list):
                raise ValueError("'data' type must be list!!!")
            objs = []
            for item in data:
                serializer = obj_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                objs.append(obj(**item))
            obj.objects.bulk_create(objs)
        except Exception as e:
            get_error_status_code(e, results)

        return self.get_results(results, need_results=need_results)
