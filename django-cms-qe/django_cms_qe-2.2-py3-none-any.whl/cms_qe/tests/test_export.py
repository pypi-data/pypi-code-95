import csv
import io
import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from pytest_data import use_data

from ..export import export_data, export_file, get_supported_export_types


class ModelAdmin:
    list_display = ('foo',)

    def foo(self, obj):
        return 'foo property'


class ExportDataAdmin(ModelAdmin):

    def export_data(self, export_type, queryset):
        return 'foo export_data'


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_csv'})
def test_export_data_as_csv(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('csv', ModelAdmin(), queryset)
    data = list(csv.reader(io.StringIO(data)))
    assert len(data) == 2
    assert 'test_export_data_as_csv' in data[1]
    assert 'foo property' in data[1]


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_tsv'})
def test_export_data_as_tsv(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('tsv', ModelAdmin(), queryset)
    data = list(csv.reader(io.StringIO(data), delimiter='\t'))
    assert len(data) == 2
    assert 'test_export_data_as_tsv' in data[1]
    assert 'foo property' in data[1]


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_json'})
def test_export_data_as_json(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('json', ModelAdmin(), queryset)
    data = json.loads(data)
    assert len(data) == 1
    assert data[0]['username'] == 'test_export_data_as_json'
    assert data[0]['foo'] == 'foo property'


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_json'})
def test_export_data_admin_function(user):
    User = get_user_model()
    queryset = User.objects.all()
    data = export_data('foo', ExportDataAdmin(), queryset)
    assert data == 'foo export_data'


@pytest.mark.django_db
@use_data(user_data={'username': 'test_export_data_as_json'})
def test_export_file():
    User = get_user_model()
    queryset = User.objects.all()
    response = export_file('csv', ModelAdmin(), queryset)
    assert response['content-disposition'] == 'attachment; ' \
        'filename="export.csv"'
    assert response.content == b'ID,password,last login,superuser ' \
        b'status,username,first name,last name,email address,staff ' \
        b'status,active,date joined,groups,user permissions,foo\r\n'


def test_get_supported_export_types():
    with patch('cms_qe.export.getattr') as mock_getattr:
        mock_getattr.side_effect = [
            'csv', 'html', 'json', 'latex', 'ods', 'rst', 'tsv', 'xls',
            'xlsx', 'yaml']
        data = get_supported_export_types()
    assert sorted(data.keys()) == [
        'csv', 'html', 'json', 'latex', 'ods', 'rst', 'tsv', 'xls', 'xlsx',
        'yaml']
    assert data['csv'].mimetype == 'text/csv'
    assert data['csv'].label == 'Export selected as CSV'


def test_get_supported_export_types_import_error():
    with patch('cms_qe.export.getattr') as mock_getattr:
        mock_getattr.side_effect = ImportError()
        data = get_supported_export_types()
    assert data == {}


def test_get_supported_export_types_attribute_error():
    with patch('cms_qe.export.getattr') as mock_getattr:
        mock_getattr.side_effect = AttributeError()
        data = get_supported_export_types()
    assert data == {}
