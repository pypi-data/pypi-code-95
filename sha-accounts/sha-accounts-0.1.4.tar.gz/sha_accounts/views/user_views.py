from rest_framework.decorators import action
from rest_framework.status import HTTP_201_CREATED
from rest_framework.response import Response
from djrest_wrapper.interfaces import BaseViewSet
from djrest_wrapper.decorators import serializer_validation
from ..models.user_models import User
from ..signals import user_logged_in, user_logged_out
from ..serializers.user_serializers import (
    UserSignUpRequest, UserSignUpResponse, UserSignInRequest,
    UserSignInResponse, UserListResponse, UserUpdateRequest,
    UserUpdateResponse, UserChangePasswordRequest,)
from ..permissions import IsAuthenticatedAndOwner, IsAdmin


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    page_result_key = 'users'
    serializer_action_classes = {
        'create': {
            'req': UserSignUpRequest,
            'res': UserSignUpResponse,
        },
        'retrieve': {
            'res': UserSignUpResponse,
        },
        'signin': {
            'req': UserSignInRequest,
            'res': UserSignInResponse,
        },
        'list': {
            'res': UserListResponse,
        },
        'update': {
            'req': UserUpdateRequest,
            'res': UserUpdateResponse,
        },
        'partial_update': {
            'req': UserUpdateRequest,
            'res': UserUpdateResponse,
        },
        'change_password': {
            'req': UserChangePasswordRequest,
        }
    }
    permission_action_classes = {
        'retrieve': [IsAuthenticatedAndOwner | IsAdmin],
        'update': [IsAuthenticatedAndOwner | IsAdmin],
        'partial_update': [IsAuthenticatedAndOwner | IsAdmin],
        'list': [IsAdmin],
        'change_password': [IsAuthenticatedAndOwner, ],
    }

    @serializer_validation
    def create(self, request, *args, **kwargs):
        reqser = self.get_serializer(data=request.data)
        reqser.is_valid(raise_exception=True)
        model = self.perform_create(reqser)
        model.access_token = user_logged_in.send(sender=User, user=model)[0][1]
        resser = self.get_serializer_response()(model)
        return Response(
            data={model.__class__.__name__.lower(): resser.data},
            status=HTTP_201_CREATED)

    @action(detail=False, methods=['POST'],
            url_name='signin', url_path='signin')
    @serializer_validation
    def signin(self, request, *args, **kwargs):
        reqser = self.get_serializer(data=request.data)
        reqser.is_valid(raise_exception=True)
        user = reqser.login()
        user.access_token = user_logged_in.send(sender=User, user=user)[0][1]
        resser = self.get_serializer_response()(user)
        return Response(data={user.__class__.__name__.lower(): resser.data})

    @action(detail=False, methods=['GET'],
            url_name='signout', url_path='signout')
    def signout(self, request, *args, **kwargs):
        user_logged_out.send(sender=User, request=request)
        return Response(data={})

    @action(detail=False, methods=['POST'],
            url_name='change-password', url_path='change-password')
    @serializer_validation
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_changed = serializer.change_password(id=request.user.id)
        if is_changed:
            user_logged_out.send(sender=User, request=request)
            return Response(data={})
