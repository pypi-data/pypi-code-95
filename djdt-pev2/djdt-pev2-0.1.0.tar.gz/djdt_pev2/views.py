import datetime
import json
import uuid
from logging import getLogger

from debug_toolbar.decorators import require_show_toolbar, signed_data_view
from django.conf import settings
from django.core.cache import cache
from django.http.response import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.template.response import SimpleTemplateResponse
from django.urls import reverse
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt

from djdt_pev2.forms import Pev2SQLSelectForm

logger = getLogger("djdt_pev2")


@require_show_toolbar
@xframe_options_sameorigin
def pev2_explain_iframe(request, plan_id):
    if not plan_id:
        return HttpResponseBadRequest("Missing result UUID ")

    context = cache.get(f"SQL_EXPLAIN:{plan_id}")

    return SimpleTemplateResponse("djdt_pev2/panels/pev_iframe.html", context=context)


def process_view(request, verified_data, sql_template):
    """Returns the output of the SQL EXPLAIN on the given query"""
    form = Pev2SQLSelectForm(verified_data)

    if form.is_valid():
        sql = form.cleaned_data["sql"]
        params = form.cleaned_data["params"]
        vendor = form.connection.vendor
        if vendor != "postgresql":
            raise NotImplementedError("Only postgresql is supported")
        with form.cursor as cursor:
            cursor.execute(sql_template.format(sql), params)
            result = cursor.fetchall()

        plan_id = str(uuid.uuid4())
        created = datetime.datetime.now()
        context = {
            "plan": json.dumps(result[0][0]),
            "plan_title": f"Untitled Plan - {created}",
            "created": created,
            "sql": sql,
            "formatted_sql": form.reformat_sql(),
            "duration": form.cleaned_data["duration"],
            "alias": form.cleaned_data["alias"],
            "stacktrace": form.cleaned_data["stacktrace"],
            "plan_id": plan_id,
            "url": request.build_absolute_uri(
                reverse("djdt:pev2_visualize", args=(plan_id,))
            ),
        }
        cache.set(
            f"SQL_EXPLAIN:{plan_id}",
            context,
            timeout=getattr(settings, "PEV2_SQL_ANALYZE_TIMEOUT", 24 * 60 * 60),
        )
        context["request"] = request
        content = render_to_string("djdt_pev2/panels/sql_explain.html", context)
        return JsonResponse({"content": content})
    return HttpResponseBadRequest("Form errors")


@csrf_exempt
@require_show_toolbar
@signed_data_view
def sql_analyze(request, verified_data):
    return process_view(
        request,
        verified_data,
        "EXPLAIN (ANALYZE, COSTS, VERBOSE, BUFFERS, FORMAT JSON) {}",
    )


@csrf_exempt
@require_show_toolbar
@signed_data_view
def sql_explain(request, verified_data):
    return process_view(
        request, verified_data, "EXPLAIN (COSTS, VERBOSE, FORMAT JSON) {}"
    )
