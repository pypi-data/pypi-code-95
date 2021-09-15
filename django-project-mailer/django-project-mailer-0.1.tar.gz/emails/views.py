# from rest_framework import viewsets
# from rest_framework.generics import get_object_or_404
# from .serializers import *
# from rest_framework import status
# from django.apps import apps
# from rest_framework.response import Response
# from .tasks import *


# # Create your views here.

# class EmailSettingAPIView(viewsets.ModelViewSet):
#     serializer_class = EmailSerializers
#     queryset = EmailModel.objects.all()

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)

#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# class EmailReminderView(viewsets.ModelViewSet):
#     serializer_class = EmailReminderSerializer
#     queryset = EmailReminder.objects.all()

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         data = serializer.data
#         if not List.objects.filter(list=data.get('modules')).exists():
#             List.objects.create(list=data.get('modules'))
#             return Response('success')
#         return Response('already exist')

#     def destroy(self, request, pk=None, *args, **kwargs):
#         queryset = EmailReminder.objects.all()
#         reminder = get_object_or_404(queryset, pk=pk)
#         reminder.is_deleted = True
#         reminder.save()
#         serializer = EmailReminderSerializer(reminder)
#         return Response(serializer.data)


# class PushReminderView(viewsets.ModelViewSet):
#     serializer_class = PushReminderSerializer
#     queryset = PushReminder.objects.all()

#     def destroy(self, request, pk=None, *args, **kwargs):
#         queryset = PushReminder.objects.all()
#         reminder = get_object_or_404(queryset, pk=pk)
#         reminder.is_deleted = True
#         reminder.save()
#         serializer = PushReminderSerializer(reminder)
#         return Response(serializer.data)


# class PolicyView(viewsets.ModelViewSet):
#     serializer_class = PolicySerializer
#     queryset = Policies.objects.all()


# class ModuleView(viewsets.ModelViewSet):
#     serializer_class = ModuleSerializer
#     queryset = Modules.objects.all()

#     def create(self, request, *args, **kwargs):
#         app_models = [model.__name__ for model in apps.get_models()]
#         print(app_models)
#         count = len(app_models)
#         print(count)
#         for i in range(count):
#             print(i)
#             module = Modules.objects.create(modules=app_models[i])
#             module.save()
#         # return "module"


from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from .serializers import *
from rest_framework import status
from django.apps import apps
from rest_framework.response import Response
from .tasks import *


# Create your views here.

class EmailSettingAPIView(viewsets.ModelViewSet):
    serializer_class = EmailSerializers
    queryset = EmailModel.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class EmailReminderView(viewsets.ModelViewSet):
    serializer_class = EmailReminderSerializer
    queryset = EmailReminder.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = serializer.data
        if not List.objects.filter(list=data.get('modules')).exists():
            List.objects.create(list=data.get('modules'))
            return Response('success')
        return Response('already exist')

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = EmailReminder.objects.all()
        reminder = get_object_or_404(queryset, pk=pk)
        reminder.is_deleted = True
        reminder.save()
        serializer = EmailReminderSerializer(reminder)
        return Response(serializer.data)


class PushReminderView(viewsets.ModelViewSet):
    serializer_class = PushReminderSerializer
    queryset = PushReminder.objects.all()

    def destroy(self, request, pk=None, *args, **kwargs):
        queryset = PushReminder.objects.all()
        reminder = get_object_or_404(queryset, pk=pk)
        reminder.is_deleted = True
        reminder.save()
        serializer = PushReminderSerializer(reminder)
        return Response(serializer.data)


class PolicyView(viewsets.ModelViewSet):
    serializer_class = PolicySerializer
    queryset = Policies.objects.all()


class ModuleView(viewsets.ModelViewSet):
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


class User(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = UserEmails.objects.all()
