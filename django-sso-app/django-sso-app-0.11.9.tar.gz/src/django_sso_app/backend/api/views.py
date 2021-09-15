import logging

from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from ...core.permissions import is_staff
from ...core.apps.users.serializers import UserSerializer
from ...core.apps.groups.models import Group
from ...core.apps.groups.serializers import GroupSerializer
from ...core.apps.services.models import Service
from ...core.apps.services.serializers import ServiceSerializer

from ..views import local_space_available, CURRENT_DIR, logger

from django_sso_app import dist_name, __version__, app_settings

logger = logging.getLogger('django_sso_app.backend.api')


class StatsView(APIView):
    """
    Return instance stats
    """

    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            health_status = 'green'

            user_types = Group.objects.filter(name__in=app_settings.USER_TYPES)
            services = Service.objects.filter(is_public=True)

            context = {
                'request': request
            }

            data = {
                'app_name': dist_name,
                'deployment_environment': settings.DEPLOYMENT_ENV,
                'revision': settings.REPOSITORY_REV,
                'version': __version__,

                'user': UserSerializer(request.user, context=context).data if request.user.is_authenticated else None,

                'user_types': GroupSerializer(user_types, many=True, context=context).data,

                'services': ServiceSerializer(services, many=True, context=context).data,

                'meta': str(request.META.items())
            }

            if is_staff(request.user):
                free_space_mb = int(local_space_available(CURRENT_DIR) / (1024 * 1024))

                logger.info(
                    'Free space (MB): {}.'.format(free_space_mb))

                if free_space_mb > 200:
                    health_status = 'green'
                else:
                    if free_space_mb < 100:
                        health_status = 'yellow'
                    else:
                        health_status = 'red'

                data['free_space_mb'] = free_space_mb

            data['status'] = health_status

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            err_msg = str(e)
            logger.exception('Error getting stats {}'.format(err_msg))
            return Response(err_msg, status.HTTP_500_INTERNAL_SERVER_ERROR)


schema_view = get_schema_view(
   openapi.Info(
      title=dist_name,
      default_version='v1',
   ),
   public=True,
   permission_classes=(AllowAny,),
)
