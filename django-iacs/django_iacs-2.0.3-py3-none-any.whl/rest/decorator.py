from functools import wraps
from typing import Type

from rest_framework.serializers import Serializer


def action_name(name=None, **kwargs):
    assert name is not None, (
        "@action_name() missing required argument: 'name'"
    )

    user_default = kwargs.get('user_default', False)

    def decorator(func):
        func.action_name = name
        func.user_default = user_default
        return func

    return decorator


def request_params_validate(serializer_class: Type[Serializer]):
    def func1(origin_function):
        @wraps(origin_function)
        def func2(view_set, request, *args, **kwargs):
            params = view_set.get_params()
            s = serializer_class(data=params)
            s.is_valid(raise_exception=True)
            validated_params = s.save()
            request.validated_params = validated_params
            request.validated_data = s.validated_data
            return origin_function(view_set, request, *args, **kwargs)

        return func2

    return func1
