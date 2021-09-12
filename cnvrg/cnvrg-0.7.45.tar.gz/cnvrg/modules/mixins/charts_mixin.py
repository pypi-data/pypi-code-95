import cnvrg.helpers.apis_helper as apis_helper
from cnvrg.helpers.url_builder_helper import url_join
from cnvrg.helpers.param_helper import wrap_into_list
from cnvrg.helpers import logger_helper
from typing import AnyStr, List

class ChartsMixin(object):

    ### Verifiers
    def __verify_same_type(self, payload):
        if len(set([o.__class__ for o in payload])) > 1:
            raise ValueError("Got two charts from different type.")

    def __inflate_y_ticks(self, data, y_ticks):
        if y_ticks: return y_ticks
        for series in data:
            if series.y_ticks: return series.y_ticks

    def __inflate_x_ticks(self, data, x_ticks):
        if x_ticks: return x_ticks
        for series in data:
            if series.x_ticks: return series.x_ticks

    def __only_one_heatmap(self, data: List):
        heatmaps = len(list(filter(lambda o: o.chart_type() == 'heatmap', data)))
        if heatmaps > 1:
            raise ValueError("Can't generate chart with more than a single heatmap")

    def __add_series_name(self, data):
        for idx, series in enumerate(data):
            series.set_series_index(idx)

    def log_chart(self, key: AnyStr, data, group=None, step=None, title: AnyStr=None,
                  x_axis: AnyStr=None, y_axis: AnyStr=None, y_ticks: List=None, x_ticks: List=None):
        data = wrap_into_list(data)
        self.__verify_same_type(data)
        self.__only_one_heatmap(data)
        self.__add_series_name(data)
        y_ticks = self.__inflate_y_ticks(data, y_ticks)
        x_ticks = self.__inflate_x_ticks(data, x_ticks)

        additional_params = {}

        if data[0].chart_type() == 'heatmap':
            chart = data[0]
            if chart.color_stops:
                additional_params["stops"] = chart.color_stops

        if data[0].chart_type() == 'bar':
            chart = data[0]
            if chart.colors:
                additional_params["colors"] = chart.colors

        if data[0].chart_type() == 'heatmap' or data[0].chart_type() == 'bar':
            chart = data[0]
            if chart.max:
                additional_params["max"] = chart.max
            if chart.min:
                additional_params["min"] = chart.min

        serieses = [o.as_series() for o in data]
        resp = self.__create_chart(
            key=key,
            group=group,
            step=step,
            chart_type=data[0].chart_type(),
            serieses=serieses,
            title=title,
            x_axis=x_axis,
            y_axis=y_axis,
            x_ticks=x_ticks,
            y_ticks=y_ticks,
            **additional_params
        )
        if resp.get("status") == 200:
            logger_helper.log_message("Chart {tag} created successfully.".format(tag=resp.get("tag")))
        else:
            logger_helper.log_message(resp.get("error"))

    def __create_chart(self, key, group, step, chart_type, serieses, title, x_axis, y_axis, x_ticks, y_ticks, **kwargs):
        data = {
            "chart": {
                "chart_type": chart_type,
                "title": title,
                "group": group,
                "step": step,
                "key": key,
                "serieses": serieses,
                "x_axis": x_axis,
                "y_axis": y_axis,
                "x_ticks": x_ticks,
                "y_ticks": y_ticks,
                **kwargs,
            }
        }
        resp = apis_helper.post(url_join(self._base_url(), 'charts'), data=data)
        return resp