from numpy import linspace
from scipy.interpolate import interp1d


class Interpolator:
    """
    Базовый класс интерполятора
    """

    def __init__(self, points=100):
        self.points = points

    def approximate(self, x, y):
        pass


class Quadratic(Interpolator):
    """
    Квдратичный интерполятор
    """

    def gen_x_axis(self, start, end):
        """
        Генерирует набор точек по оси абсцисс
        :param start:
        :param end:
        :return:
        """
        return linspace(start, end, self.points)

    def approximate(self, x, y):
        points = interp1d(x, y, kind='quadratic')
        x = linspace(min(x), max(x), self.points)
        y = points(x)

        return x, y
