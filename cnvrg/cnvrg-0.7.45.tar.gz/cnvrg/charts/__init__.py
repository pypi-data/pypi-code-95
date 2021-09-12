from typing import List, AnyStr
import math

class BasicChart(object):
    def __init__(self, name="default"):
        self.__name = name

    def _sanitize_list(self, l):
        if hasattr(l, 'tolist'):
            return l.tolist()
        return l

    def set_series_index(self, idx):
        self.__name = self.__name or "Series {}".format(idx)

    @property
    def x_ticks(self):
        return None

    @property
    def y_ticks(self):
        return None

    @property
    def data(self):
        return []

    def as_series(self):
        return {
            "name": self.__name,
            "data": self.data
        }


class Bar(BasicChart):
    def __init__(self, x: List, y: List, name: AnyStr=None, min_val=None, max_val=None, colors=None):
        super(Bar, self).__init__(name=name)
        self.__x = self._sanitize_list(x)
        self.__y = self._sanitize_list(y)
        self._min = min_val
        self._max = max_val
        self._colors = self._validate_colors(colors)

    def _validate_colors(self, colors):
        if colors is None:
            return []
        elif type(colors) is not list:
            raise ValueError("Colors should be in format: ['#3060cf', '#fffbbc', ...]")
        return colors

    @classmethod
    def chart_type(cls):
        return "bar"

    @property
    def x_ticks(self):
        return self.__x

    @property
    def data(self):
        return self.__y

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max

    @property
    def colors(self):
        return self._colors


class Heatmap(BasicChart):
    def __init__(self, z: List, name: AnyStr=None, color_stops=None, min_val=None, max_val=None):
        super(Heatmap, self).__init__(name=name)
        self._x = []
        self._y = []
        self._z = []
        self._tokenize_list(self._sanitize_list(z))
        self._color_stops = self._validate_stops(color_stops)
        self._min = min_val
        self._max = max_val

    def _validate_stops(self, color_stops):
        if color_stops is None:
            return []
        elif type(color_stops) is not list:
            raise ValueError("Color stops should be in format: [[0, '#3060cf'], [0.5, '#fffbbc'], ...]")

        for stop in color_stops:
            if type(stop) is not list or len(stop) != 2:
                raise ValueError("Color stops should be in format: [[0, '#3060cf'], [0.5, '#fffbbc'], ...]")

        return color_stops

    def _tokenize_list(self, l):
        for q in l:
            if len(q) == 2:
                (x, y), z = q
            elif len(q) == 3:
                x, y, z = q
            else:
                raise ValueError("Heatmap only support in values in type of ((x,y),z) or (x,y,z)")
            if math.isnan(z):
                continue
            if x not in self._x:
                self._x.append(x)
            if y not in self._y:
                self._y.append(y)
            self._z.append((x, y, z))
        self._x = sorted(self._x)
        self._y = sorted(self._y)
        self._z = [(self._x.index(x), self._y.index(y), z) for x, y, z in self._z]

    @classmethod
    def chart_type(cls):
        return "heatmap"

    @property
    def x_ticks(self):
        return self._x

    @property
    def y_ticks(self):
        return self._y

    @property
    def data(self):
        return self._z

    @property
    def color_stops(self):
        return self._color_stops

    @property
    def min(self):
        return self._min

    @property
    def max(self):
        return self._max


class MatrixHeatmap(Heatmap):
    def __init__(self, matrix, name: AnyStr=None, color_stops=None, min_val=None, max_val=None):
        z = []
        for y in range(len(matrix)):
            for x in range(len(matrix[0])):
                z.append((x, y, matrix[y][x]))
        super(MatrixHeatmap, self).__init__(z, name, color_stops, min_val, max_val)


class Scatterplot(BasicChart):
    def __init__(self, x: List, y: List, name: AnyStr=None):
        super(Scatterplot, self).__init__(name=name)
        self._x = self._sanitize_list(x)
        self._y = self._sanitize_list(y)

    @classmethod
    def chart_type(cls):
        return "scatter"

    @property
    def data(self):
        return list(zip(self._x, self._y))


class CategoricalScatterplot(Scatterplot):

    @property
    def x_axis(self):
        return sorted(list(set(self._x)))

    @property
    def y_axis(self):
        return sorted(list(set(self._y)))


    @property
    def data(self):
        x_ax = self.x_axis
        y_ax = self.y_axis
        x_i = list(map(lambda x: x_ax.index(x), self._x))
        y_i = list(map(lambda y: y_ax.index(y), self._y))
        return list(zip(x_i, y_i))


