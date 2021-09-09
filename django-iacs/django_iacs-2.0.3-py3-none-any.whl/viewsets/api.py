from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from ..rest.viewsets import GenericViewSet
from ..models import Api
from ..serializers.api import ApiSerializer


# noinspection PyUnusedLocal
class ApiViewSet(GenericViewSet,
                 ListModelMixin):
    queryset = Api.objects.filter(user_default=0)
    serializer_class = ApiSerializer
    known_actions_name = {
        'list': '获取所有API'
    }

    def list(self, request, *args, **kwargs):
        groups = [api.group for api in self.queryset]
        no_repeat_groups = list(set(groups))
        no_repeat_groups.sort(key=groups.index)
        ret = []
        for name in no_repeat_groups:
            queryset = self.queryset.filter(group=name)
            serializer = self.get_serializer(queryset, many=True)
            ret.append({
                'group': name,
                'data': serializer.data
            })
        return Response(ret)
