from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
import pytest

from ..exceptions import TableDoesNotExists
from ..utils import get_model_by_table, get_models_choices, get_table_choices, get_field_type, get_filter_params


def test_get_model_by_table():
    User = get_user_model()
    model = get_model_by_table('auth_user')
    assert model is User


def test_get_model_by_table_not_found():
    with pytest.raises(TableDoesNotExists):
        get_model_by_table('table_does_not_exist')


def test_get_all_models():
    choices = get_models_choices()
    choices_admin_group = [item[1] for item in choices if item[0] == 'admin'][0]
    assert choices_admin_group == (
        ('django_admin_log', 'LogEntry'),
    )


def test_get_table_choices():
    choices = get_table_choices('auth_user')
    assert 'columns' in choices
    assert ('username', 'username', 'string') in choices['columns']


@pytest.mark.parametrize('field, expected_type', [
    (models.AutoField(), 'integer'),
    (models.BigAutoField(), 'integer'),
    (models.BigIntegerField(), 'integer'),
    (models.BooleanField(), 'boolean'),
    (models.CharField(), 'string'),
    (models.DateField(), 'string'),
    (models.DateTimeField(), 'string'),
    (models.DecimalField(), 'float'),
    (models.EmailField(), 'string'),
    (models.FloatField(), 'float'),
    (models.ForeignKey('LogEntry', on_delete=models.CASCADE), 'string'),
    (models.IntegerField(), 'integer'),
    (models.GenericIPAddressField(), 'string'),
    (models.NullBooleanField(), 'boolean'),
    (models.PositiveIntegerField(), 'integer'),
    (models.PositiveSmallIntegerField(), 'integer'),
    (models.SlugField(), 'string'),
    (models.SmallIntegerField(), 'integer'),
    (models.TextField(), 'string'),
    (models.TimeField(), 'string'),
    (models.URLField(), 'string'),
    (models.UUIDField(), 'string'),
])
def test_get_field_type(field, expected_type):
    assert get_field_type(field) == expected_type


def test_get_filter_params():
    class ForeignModel(models.Model):
        text1 = models.CharField()
        text2 = models.CharField()
        flag = models.BooleanField()
        number = models.IntegerField()

    class Model(models.Model):
        other = models.ForeignKey(ForeignModel, on_delete=models.CASCADE)
        name = models.CharField()
        active = models.BooleanField()
        age = models.IntegerField()

    args, kwds = get_filter_params(Model, {
        'other': 'abc',
        'name': 'name',
        'active': True,
        'age': 123,
        'non-existent-field': 'blah',
    })
    assert str(args) == str([
        Q() | Q(other__text1__icontains='abc') | Q(other__text2__icontains='abc')
    ])
    assert kwds == {
        'name__icontains': 'name',
        'active': True,
        'age': 123,
    }
