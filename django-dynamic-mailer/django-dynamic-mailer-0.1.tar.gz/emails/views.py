from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from .serializers import *
from rest_framework import status
from django.apps import apps
from rest_framework.response import Response


# Create your views here.

class EmailSettingAPIView(viewsets.ModelViewSet):

    """ rest view set for Email model table  """

    serializer_class = EmailSerializers
    queryset = EmailModel.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmailReminderView(viewsets.ModelViewSet):

    """ rest view set for Email reminder table for create table and destroy  """

    serializer_class = EmailReminderSerializer
    queryset = EmailReminder.objects.all()

    def create(self, request, *args, **kwargs):
        """ creating email reminder and also updating List model table from selecting modules  """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        if not List.objects.filter(list=data.get('modules')).exists():
            List.objects.create(list=data.get('modules'))
        return Response("success")

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = EmailReminder.objects.all()
        reminder = get_object_or_404(queryset, pk=pk)
        reminder.is_deleted = True
        reminder.save()
        serializer = EmailReminderSerializer(reminder)
        return Response(serializer.data)


class PolicyView(viewsets.ModelViewSet):

    """ rest view set for policy purchase table """

    serializer_class = PolicySerializer
    queryset = Policies.objects.all()


class ModuleView(viewsets.ModelViewSet):

    """ rest view set for creating all the model table  """

    serializer_class = ModuleSerializer
    queryset = Modules.objects.all()

    def create(self, request, *args, **kwargs):
        app_models = apps.all_models['emails']
        app_models_list = list(app_models.values())
        model_list = [app_models_list[i].__name__ for i in range(len(app_models_list))]
        for i in range(len(model_list)):
            module = Modules.objects.create(modules=model_list[i])
            module.save()
        return Response("success")


class UserEmailView(viewsets.ModelViewSet):

    """ rest view set for user creation model """

    serializer_class = UserEmailSerializer
    queryset = UserEmails.objects.all()
