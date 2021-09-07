import datetime
import time

from django.core.paginator import Paginator, Page, EmptyPage
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.cache import cache
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt

from kirui_devserver.backend.forms import SampleForm
from kirui_devserver.backend.models import Activity


def index(request):
    form = SampleForm(request.POST or None, instance=Activity.objects.first())
    form.is_valid()
    return render(request, 'base.xml', context={'now': datetime.datetime.now(), 'form': form})


def form(request):
    print(request.POST)
    form = SampleForm(request.POST or None, instance=Activity.objects.first())
    if form.is_valid():
        form = SampleForm(None)
        resp = HttpResponseRedirect('/backend/table/')
        resp.status_code = 340
        return resp
    else:
        data = get_template('form.xml').render(context={'form': form}, request=request, to='jsx')
        resp = HttpResponse(data)
        resp.status_code = 403
        return resp

    return render(request, 'form.xml', context={'now': datetime.datetime.now(), 'form': form})


def tests(request):
    return render(request, 'tests.html')


def poll_filesystem_changes(request):
    return HttpResponse(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def data(request):
    return render(request, 'index.xml', context={'iterable': [1, 2, 3], 'value': 8})


def modal(request):
    form = SampleForm(request.POST or None)
    form.now = datetime.datetime.now()
    if form.is_valid():
        pass

    data = get_template('modal.xml').render(context={'form': form}, request=request, to='jsx')
    resp = HttpResponse(data)
    if form.is_valid():
        resp.status_code = 200
    else:
        resp.status_code = 403

    return resp


def table(request):
    data = []
    for row in range(1, 20):
        data.append({'first': f'{row}.1', 'second': f'{row}.2'})
    return render(request, 'table.xml', context={'data': data})


def panel(request):
    form = SampleForm(request.POST or None)
    if form.is_valid():
        pass

    return render(request, 'panel.xml', context={'now': datetime.datetime.now(), 'form': form, 'page': None})


TABLE_ROWS = [{'first': f'{_}.1', 'second': f'{_}.2'} for _ in range(0, 100)]


class CustomPage(Page):
    def next_page_number(self):
        try:
            return self.paginator.validate_number(self.number + 1)
        except EmptyPage:
            return ''

    def previous_page_number(self):
        try:
            return self.paginator.validate_number(self.number - 1)
        except EmptyPage:
            return ''


class CustomPaginator(Paginator):
    def _get_page(self, *args, **kwargs):
        return CustomPage(*args, **kwargs)


def panel_data(request):
    form = SampleForm(request.POST or None)
    if form.is_valid():
        TABLE_ROWS = [{'first': f'{_}.1 {form.cleaned_data["masodik"]}', 'second': f'{_}.2'} for _ in range(0, 100)]
        paginate_to = request.POST.get('paginate_to')
        paginate_to = paginate_to or 1
        paginate_to = int(paginate_to)
        p = CustomPaginator(TABLE_ROWS, 20)
        page = p.page(paginate_to)
    else:
        page = None

    data = get_template('panel_data.xml').render(context={'now': datetime.datetime.now(), 'form': form, 'page': page}, request=request)
    resp = JsonResponse(data, safe=False)
    return resp
