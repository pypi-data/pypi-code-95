from rest_framework.response import Response


# noinspection PyUnresolvedReferences
class PartialFieldsListModelMixin:

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page,
                                             many=True,
                                             fields=self.simple_serialize_fields)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
