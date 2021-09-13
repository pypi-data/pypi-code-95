import pprint

time_unit_factor = {
    'h': 1 / 3600,
    "min": 1 / 60,
    "s": 1,
    "ms": 1000
}


def _format_time(time_value, time_unit=None, round_value=None):
    if time_unit is None:
        time_factor = 1
    else:
        time_factor = time_unit_factor[time_unit]

    format_time = time_value * time_factor

    if round_value is not None:
        format_time = round(format_time, round_value)

    return format_time


class Timer:

    def __init__(self, timer_name):
        self.name = timer_name
        self.time_ms = 0
        self.count_call = 0
        self.function_in_it = {}
        self.decorator_time = 0

    def add_decorator_time(self, execute_time):
        self.decorator_time += execute_time

    def add_child_timer(self, child_timer_object):
        self.function_in_it[child_timer_object.name] = child_timer_object

    def add_time(self, execute_time):
        self.time_ms += execute_time
        self.count_call += 1

    def minus_time(self, execute_time):
        self.time_ms -= execute_time

    def get_children_name(self):
        return self.function_in_it.keys()

    def get_child_timer(self, child_name):
        if child_name in self.function_in_it:
            return self.function_in_it[child_name]
        else:
            raise Exception("This is not a child of {}".format(self.name))

    def _print_function_timer(self, indent=0, time_unit='ms'):
        if self.function_in_it:
            for function_timer_name, function_timer in self.function_in_it.items():
                function_timer._print_function_timer(indent=indent + 1, time_unit=time_unit)

    def _print_timer(self, indent, time_unit='ms', round_value=3):
        if indent:
            indent_txt = '\t' * indent
        else:
            indent_txt = ''

        str_return = '{indent_txt}{function_name}:'.format(
            indent_txt=indent_txt,
            function_name=self.name
        )
        if self.count_call:
            format_time = round(self.time_ms * time_unit_factor[time_unit], round_value)
            str_return = '{str_return}time ({time_unit}): {time}, nb call: {nb_call}, time by call, {time_call}'.format(
                str_return=str_return,
                time=format_time,
                time_unit=time_unit,
                nb_call=self.count_call,
                time_call=round(format_time / self.count_call, round_value)
            )

        # add decorator time
        decorator_time = round(self.decorator_time * time_unit_factor[time_unit], round_value)
        str_return += ', decorator time: {decorator_time}'.format(decorator_time=decorator_time)
        return str_return

    def _get_feature(self, time_field_list, indent=0, path=None, path_tree_dict=None):

        if path is None:
            path = []

        if path_tree_dict is None:
            path_tree_dict = {}

        if indent:
            indent_txt = '\t' * indent
        else:
            indent_txt = ''

        path = tuple(path + [self.name])
        feature = {
            "attributes": {
                'function_name': '{indent_txt}{name}'.format(
                    indent_txt=indent_txt.expandtabs(),
                    name=self.name
                ),
                'path': path
            }
        }
        if self.count_call:
            time_value = self.time_ms
            format_time_field_name, format_decorator_time_field_name, format_mean_time_field_name, format_true_time_field_name, format_true_mean_time_field_name = time_field_list
            feature['attributes'][format_time_field_name] = time_value
            feature['attributes'][format_decorator_time_field_name] = self.decorator_time
            feature['attributes']['count_call'] = self.count_call
            feature['attributes'][format_mean_time_field_name] = time_value / self.count_call

            # compute true time
            if path in path_tree_dict:
                feature['attributes'][format_true_time_field_name] = time_value - path_tree_dict[path]
                feature['attributes'][format_true_mean_time_field_name] = feature['attributes'][format_true_time_field_name] / self.count_call
        return feature

    def _get_features(self, time_field_list, indent=0, path=[], path_tree_dict={}):
        if self.function_in_it:
            path = path + [self.name]
            for function_timer_name, function_timer in self.function_in_it.items():
                yield function_timer._get_feature(time_field_list=time_field_list, indent=indent, path=path,
                                                  path_tree_dict=path_tree_dict)
                for feature in function_timer._get_features(time_field_list=time_field_list, indent=indent + 1, path=path,
                                                            path_tree_dict=path_tree_dict):
                    yield feature

    def _get_associate_decorator_time_for_function_path(self, function_dict=None, function_path=None):
        """
        Create dict with path in key and decorator time associate to given path
        :param function_dict:
        :param function_path:
        :return:
        """

        if function_dict is None:
            function_dict = {}
        if function_path is None:
            function_path = []

        # function_path.append(self.name)
        function_dict[tuple(function_path + [self.name])] = {'decorator_time': self.decorator_time}

        if self.function_in_it:
            function_path = function_path + [self.name]
            for child_name, child in self.function_in_it.items():
                child_function_dict = child._get_associate_decorator_time_for_function_path(
                    function_dict=function_dict,
                    function_path=function_path)
                for key, value in child_function_dict.items():
                    function_dict[key] = value

        return function_dict

    def _get_sum_of_decorator_time_for_function_path(self, function_path_decorator_time):
        """
        Add decorator time from all child to function_path

        :param function_path_decorator_time:
        :return:
        """
        path_list = function_path_decorator_time.keys()
        path_tree_dict = {}
        for path_tuple in path_list:
            request_path_list = []
            for path_value in path_tuple:
                request_path_list.append(path_value)
                request_path_tuple = tuple(request_path_list)
                len_request_path_tuple = len(request_path_list)
                if tuple(request_path_tuple) not in path_tree_dict:
                    # create new entry
                    path_tree_dict[request_path_tuple] = 0  # zero because value is added in second loop
                    # loop on path_list to add child decorator time
                    for path_tuple_2 in path_list:
                        # if child path
                        if request_path_tuple == path_tuple_2[:len_request_path_tuple] and len(
                                path_tuple_2) > len_request_path_tuple:
                            # add child decorator time
                            path_tree_dict[request_path_tuple] += function_path_decorator_time[path_tuple_2][
                                'decorator_time']

        return path_tree_dict

    def _get_format_field_time(self, features_list, time_field_list, time_unit, round_value=3):
        """
        format time field to given time unit

        :param features_list:
        :param time_field_list:
        :param time_unit:
        :return:
        """

        for feature in features_list:
            feature_attributes = feature['attributes']
            del feature_attributes['path']
            for time_field in time_field_list:
                if time_field in feature_attributes:
                    feature_attributes[time_field] = _format_time(
                        feature_attributes[time_field],
                        time_unit=time_unit,
                        round_value=round_value
                    )

        return features_list

    def print(self, time_unit='ms', round_value=3):

        # we create a dictionary that store decorator time for each call
        function_path_decorator_time = self._get_associate_decorator_time_for_function_path()
        # we create a dictionary that sum decorator time for function
        path_tree_dict = self._get_sum_of_decorator_time_for_function_path(
            function_path_decorator_time=function_path_decorator_time
        )
        # create features that store time information
        # compute time field
        format_time_field_name = 'time_{}'.format(time_unit)
        format_mean_time_field_name = 'mean_time_by_call_{}'.format(time_unit)
        format_decorator_time_field_name = 'decorator_time_{}'.format(time_unit)
        format_true_time_field_name = 'true_{}'.format(format_time_field_name)
        format_true_mean_time_field_name = 'true_{}'.format(format_mean_time_field_name)
        time_field_list = [
            format_time_field_name,
            format_mean_time_field_name,
            format_decorator_time_field_name,
            format_true_time_field_name,
            format_true_mean_time_field_name
        ]
        indent = 0
        features_list = [self._get_feature(time_field_list=time_field_list, indent=indent, path=[], path_tree_dict=path_tree_dict)]
        indent = 1
        features_list += [feature for feature in
                          self._get_features(time_field_list=time_field_list, indent=indent, path=[], path_tree_dict=path_tree_dict)]

        # format time field in given unit
        features_list = self._get_format_field_time(features_list, time_field_list, time_unit, round_value=round_value)

        # we print result
        from geoformat.conversion.feature_conversion import feature_list_to_geolayer
        from geoformat.explore_data.print_data import print_features_data_table
        print(print_features_data_table(geolayer=feature_list_to_geolayer(features_list, geolayer_name='timer')))
