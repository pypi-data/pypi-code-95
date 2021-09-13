from rest_framework import serializers
from . import models
from django.forms.fields import FileField

#
# class CompanySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = models.Company
#         exclude = ['id', 'image']
#
