from collections import defaultdict
from copy import copy
from pprint import saferepr

import debug_toolbar.panels.sql.views as sql_views
from debug_toolbar.forms import SignedDataForm
from debug_toolbar.panels.sql.panel import (
    SQLPanel,
    get_isolation_level_display,
    get_transaction_status_display,
)
from debug_toolbar.panels.sql.utils import contrasting_color_generator, reformat_sql
from debug_toolbar.utils import render_stacktrace
from django.conf.urls import url
from django.urls.conf import path

from .. import views
from ..forms import Pev2SQLSelectForm


class Pev2SQLPanel(SQLPanel):

    template = "djdt_pev2/panels/sql.html"

    @classmethod
    def get_urls(cls):
        return [
            url(r"^sql_select/$", sql_views.sql_select, name="sql_select"),
            url(r"^sql_explain/$", views.sql_explain, name="sql_explain"),
            url(r"^sql_analyze/$", views.sql_analyze, name="sql_analyze"),
            url(r"^sql_profile/$", sql_views.sql_profile, name="sql_profile"),
            path(
                "pev2_explain_iframe/<uuid:plan_id>/",
                views.pev2_explain_iframe,
                name="pev2_visualize",
            ),
        ]

    def generate_stats(self, request, response):
        colors = contrasting_color_generator()
        trace_colors = defaultdict(lambda: next(colors))
        query_similar = defaultdict(lambda: defaultdict(int))
        query_duplicates = defaultdict(lambda: defaultdict(int))

        # The keys used to determine similar and duplicate queries.
        def similar_key(query):
            return query["raw_sql"]

        def duplicate_key(query):
            raw_params = (
                () if query["raw_params"] is None else tuple(query["raw_params"])
            )
            # saferepr() avoids problems because of unhashable types
            # (e.g. lists) when used as dictionary keys.
            # https://github.com/jazzband/django-debug-toolbar/issues/1091
            return (query["raw_sql"], saferepr(raw_params))

        if self._queries:
            width_ratio_tally = 0
            factor = int(256.0 / (len(self._databases) * 2.5))
            for n, db in enumerate(self._databases.values()):
                rgb = [0, 0, 0]
                color = n % 3
                rgb[color] = 256 - n // 3 * factor
                nn = color
                # XXX: pretty sure this is horrible after so many aliases
                while rgb[color] < factor:
                    nc = min(256 - rgb[color], 256)
                    rgb[color] += nc
                    nn += 1
                    if nn > 2:
                        nn = 0
                    rgb[nn] = nc
                db["rgb_color"] = rgb

            trans_ids = {}
            trans_id = None
            i = 0
            for alias, query in self._queries:
                query_similar[alias][similar_key(query)] += 1
                query_duplicates[alias][duplicate_key(query)] += 1

                trans_id = query.get("trans_id")
                last_trans_id = trans_ids.get(alias)

                if trans_id != last_trans_id:
                    if last_trans_id:
                        self._queries[(i - 1)][1]["ends_trans"] = True
                    trans_ids[alias] = trans_id
                    if trans_id:
                        query["starts_trans"] = True
                if trans_id:
                    query["in_trans"] = True

                query["alias"] = alias
                if "iso_level" in query:
                    query["iso_level"] = get_isolation_level_display(
                        query["vendor"], query["iso_level"]
                    )
                if "trans_status" in query:
                    query["trans_status"] = get_transaction_status_display(
                        query["vendor"], query["trans_status"]
                    )

                # >>>>> BEGIN PEV2 CHANGES
                query["stacktrace"] = render_stacktrace(query["stacktrace"])
                query["form"] = SignedDataForm(
                    auto_id=None, initial=Pev2SQLSelectForm(initial=copy(query)).initial
                )
                # <<<<< END PEV2 CHANGES

                if query["sql"]:
                    query["sql"] = reformat_sql(query["sql"], with_toggle=True)
                query["rgb_color"] = self._databases[alias]["rgb_color"]
                try:
                    query["width_ratio"] = (query["duration"] / self._sql_time) * 100
                except ZeroDivisionError:
                    query["width_ratio"] = 0
                query["start_offset"] = width_ratio_tally
                query["end_offset"] = query["width_ratio"] + query["start_offset"]
                width_ratio_tally += query["width_ratio"]
                i += 1

                query["trace_color"] = trace_colors[query["stacktrace"]]

            if trans_id:
                self._queries[(i - 1)][1]["ends_trans"] = True

        # Queries are similar / duplicates only if there's as least 2 of them.
        # Also, to hide queries, we need to give all the duplicate groups an id
        query_colors = contrasting_color_generator()
        query_similar_colors = {
            alias: {
                query: (similar_count, next(query_colors))
                for query, similar_count in queries.items()
                if similar_count >= 2
            }
            for alias, queries in query_similar.items()
        }
        query_duplicates_colors = {
            alias: {
                query: (duplicate_count, next(query_colors))
                for query, duplicate_count in queries.items()
                if duplicate_count >= 2
            }
            for alias, queries in query_duplicates.items()
        }

        for alias, query in self._queries:
            try:
                (query["similar_count"], query["similar_color"]) = query_similar_colors[
                    alias
                ][similar_key(query)]
                (
                    query["duplicate_count"],
                    query["duplicate_color"],
                ) = query_duplicates_colors[alias][duplicate_key(query)]
            except KeyError:
                pass

        for alias, alias_info in self._databases.items():
            try:
                alias_info["similar_count"] = sum(
                    e[0] for e in query_similar_colors[alias].values()
                )
                alias_info["duplicate_count"] = sum(
                    e[0] for e in query_duplicates_colors[alias].values()
                )
            except KeyError:
                pass

        self.record_stats(
            {
                "databases": sorted(
                    self._databases.items(), key=lambda x: -x[1]["time_spent"]
                ),
                "queries": [q for a, q in self._queries],
                "sql_time": self._sql_time,
            }
        )
