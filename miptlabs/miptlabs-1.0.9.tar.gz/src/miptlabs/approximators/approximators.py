"""
Модуль содержаший базовые апроксиматоры
"""

from warnings import warn

import numpy as np
import scipy.fftpack
import scipy.optimize
from statsmodels.nonparametric.smoothers_lowess import lowess

from . import functions
from ..utils import round_to_n, format_monoid


class Approximator:
    """
    Базовый класс апроксиматор.
    Классы нужны, чтобы сохранять разные данные, во время апроксимации. Напрмер коэффициенты, ошибки.
    Для некоторых позволяют гененрировать формулу в латехе
    """

    def __init__(self, points=100, left_offset=5, right_offset=5):
        """
        :param points: количество точек, которые будут на выходе
        :param left_offset: отступ от левой гриницы диапозона
        :param right_offset: отступ от правой гриницы диапозона
        """
        self.left_offset = left_offset / 100
        self.right_offset = right_offset / 100
        self.points = points
        self.meta = []

        # Коэффициенты апроксимации
        self.koefs = []

    def _gen_x_axis_with_offset(self, start, end):
        """
        Генерирует набор точек по оси абсцисс в заданом диапозоне с учетом отступов.
        Функция нужна для внутрених нужд
        :param start: начало диапозона
        :param end: конец диапозона
        :return:
        """

        delta = end - start

        return np.linspace(start - delta * self.left_offset, end + delta * self.right_offset, self.points)

    def gen_x_axis(self, start, end):
        """
        Генерирует набор точек по оси абсцисс в заданом диапозоне
        :param start: начало диапозона
        :param end: конец диапозона
        :return:
        """

        delta = end - start

        return np.linspace(start, end, self.points)

    def approximate(self, x, y):
        """
        Функция апроксимации
        :param x: набор параметров оси x
        :param y: набор параметров оси y
        :return: набор точек на кривой апроксимации
        """
        return x, y

    def get_function(self):
        """Возвращает полученную функцию"""
        return 0

    def label(self, xvar='x', yvar='y'):
        """
        Генерирует формулу для латеха
        :param xvar: буква перемонной по оси x
        :param yvar: буква перемонной по оси y
        :return: сгенерированную формулу
        """
        return f'[{self.__class__.__name__}] function with params: {self.meta}'


class Lowess(Approximator):
    """
    Реализует алгоритм lowess.
    Предоставляет общий и гибкий подход для приближения двумерных данных.
    Подробнее http://www.machinelearning.ru/wiki/index.php?title=%D0%90%D0%BB%D0%B3%D0%BE%D1%80%D0%B8%D1%82%D0%BC_LOWESS
    Для некоторых наборов данных оченб хорошо апроксимирует кривую
    """

    def __init__(self, frac=0.35, points=100, left_offset=5, right_offset=5):
        """

        :param frac: Параметр f указывает, какая доля (fraction) данных используется в процедуре. Если f = 0.5, то только половина данных используется для оценки и влияет на результат, и тогда мы получим умеренное сглаживание. С другой стороны, если f = 0.8, то используются восемьдесят процентов данных, и сглаживание намного сильнее. Во всех случаях веса данных тем больше, чем они ближе к объекту t.
Процедура оценки использует не метод наименьших квадратов, а более устойчивый ( робастный ) метод, который принимает меры против выбросов.
        :param points: количество точек, которые будут на выходе
        :param left_offset: отступ от левой гриницы диапозона
        :param right_offset: отступ от правой гриницы диапозона
        """
        super(Lowess, self).__init__(points, left_offset, right_offset)
        self.frac = frac

    def approximate(self, x, y):
        # Нечто
        result = lowess(y, x, frac=self.frac)

        return result[:, 0], result[:, 1]


class Fourier(Approximator):
    """
    # WIP #
    Апроксимация функции с помощью преобразования фурье
    """

    def approximate(self, x, y):
        # Fourier
        x = np.array(x)
        y = np.array(y)
        w = scipy.fftpack.rfft(y)
        # f = scipy.fftpack.rfftfreq(10000, x[1] - x[0])
        spectrum = w ** 2
        cutoff_idx = spectrum < (spectrum.max() / 50000)
        w2 = w.copy()
        w2[cutoff_idx] = 0
        y = scipy.fftpack.irfft(w2)

        return x, y


class Polynomial(Approximator):
    """
    Апроксимация с помощью полинома
    Получаемая функция
    """

    def __init__(self, deg=1, points=100, left_offset=5, right_offset=5):
        """
        :param deg: степень апроскимируещего полинома
        :param points: количество точек, которые будут на выходе
        :param left_offset: отступ от левой гриницы диапозона
        :param right_offset: отступ от правой гриницы диапозона
        """
        super(Polynomial, self).__init__(points, left_offset, right_offset)
        self.deg = deg

    def approximate(self, x, y):
        poly_koefs = np.polyfit(x, y, deg=self.deg, full=True)
        self.meta = poly_koefs
        self.koefs = poly_koefs[0]
        poly = np.poly1d(poly_koefs[0])
        xs = self._gen_x_axis_with_offset(min(x), max(x))
        return xs, poly(xs)

    def get_function(self):
        return np.poly1d(self.koefs)

    def label(self, xvar='x', yvar='y'):

        # если степень равна 0, то возвращаем эту константу
        if self.deg == 0:
            return f'${yvar} = {format_monoid(self.koefs[0], True)}$'

        # списисок моноидов
        monoids = []

        # форматируем коэффициент при каждой степени, кроме первой и нулевой
        for i in range(self.deg - 1):
            monoid = f'{format_monoid(self.koefs[i])}{xvar}^{{{self.deg - i}}}'
            monoids.append(monoid)

        # форматируем коэффициент при первой степени
        monoids.append(f'{format_monoid(self.koefs[self.deg - 1])}{xvar}')

        # форматируем коэффициент при нелевой степени
        monoids.append(f'{format_monoid(self.koefs[self.deg])}')

        # объединяем в один полином
        res = ''.join(monoids)

        # убираем плюс при максимальной степени
        # FIXME неоптимизированный костыль с копирование строк
        if self.koefs[0] >= 0:
            res = res[1:]

        return f"${yvar} = {res}$"


class Linear(Polynomial):
    """
    Апроксимация с помощью прямой y=kx+b
    Получаемая функция
    """

    def __init__(self, points=100, left_offset=5, right_offset=5):
        """
        :param deg: степень апроскимируещего полинома
        :param points: количество точек, которые будут на выходе
        :param left_offset: отступ от левой гриницы диапозона
        :param right_offset: отступ от правой гриницы диапозона
        """
        super(Linear, self).__init__(1, points, left_offset, right_offset)
        # Данные
        self._x: np.ndarray = np.array([])
        self._y: np.ndarray = np.array([])
        self.__k = None
        self.__b = None

    def approximate(self, x, y):
        self._x = np.array(x)
        self._y = np.array(y)
        return super(Linear, self).approximate(x, y)

    def _brac_x(self):
        return self._x.mean()

    def _brac_y(self):
        return self._y.mean()

    def _brac_x2(self):
        return (self._x * self._x).mean()

    def _brac_y2(self):
        return (self._y * self._y).mean()

    def _brac_xy(self):
        return (self._x * self._y).mean()

    def _d_xy(self):
        return (self._x - self._x.mean()).mean() * (self._y - self._y.mean()).mean()

    def _d_xx(self):
        return np.square(self._x - self._x.mean()).mean()

    def _d_yy(self):
        return np.square(self._y - self._y.mean()).mean()

    def _k(self):
        self.__k = (self._brac_xy() - self._brac_x() * self._brac_y()) / (self._brac_x2() - self._brac_x() ** 2)
        return self.__k

    def _b(self):
        if self.__k is None:
            self._k()

        self.__b = self._brac_y() - self.__k * self._brac_x()
        return self.__b

    def _sigma_k(self):
        if self.__k is None:
            self._k()

        if len(self._x) == 2:
            return 0

        return np.sqrt(np.abs((self._d_yy() / self._d_xx() - self._k() ** 2) / (len(self._x) - 2)))

    def _sigma_b(self):
        if self.__b is None:
            self._b()

        return self._sigma_k() * np.sqrt(self._brac_x2())


class Functional(Approximator):

    def __init__(self, function, points=100, left_offset=5, right_offset=5):
        """
        :param function: функция для апроксимации
        Должна быть в виде f(x, *params), где x - переменная, params - параметры для подгона. например
            def exp(x, a, b, c):
                return a * np.exp(b * x) + c
        У этой функции будут определяться параметры a, b, c
        :param points: количество точек, которые будут на выходе
        :param left_offset: отступ от левой гриницы диапозона
        :param right_offset: отступ от правой гриницы диапозона
        """
        super(Functional, self).__init__(points, left_offset, right_offset)
        self.function = function

    def get_function(self):
        """Возвращает полученную функцию"""

        def _function(x):
            return self.function(x, *self.koefs)

        return _function

    def approximate(self, x, y):
        # пытаемся апроксимировать. если у scipy плохо получается, то оно выбрасывает ислючение RuntimeError
        try:
            self.meta = scipy.optimize.curve_fit(self.function, x, y)
            self.koefs = self.meta[0]
            xs = self._gen_x_axis_with_offset(min(x), max(x))
            ys = self.function(xs, *self.koefs)
            return xs, ys
        except RuntimeError:
            # Если вызывается исключение, то возвращаем исходные данные
            warn(f"Точки плохо подходят под апроксимацию выбранной функцией {self.function.__name__}")
            return x, y

    def label(self, xvar='x', yvar='y'):
        try:
            return f'function with params: {[round_to_n(param, 3) for param in self.koefs]}'
        except IndexError:
            return f'Функция {self.function.__name__}, которая плохо подходит'


class Exponential(Approximator):
    """
    Экспоненциальный апроксиматор
    y = a*exp(bx)+c
    """

    def approximate(self, x, y):
        # пытаемся апроксимировать. если у scipy плохо получается, то оно выбрасывает ислючение RuntimeError
        try:
            result = scipy.optimize.curve_fit(functions.exp_for_fit, x, y)
            self.meta = result
            self.koefs = self.meta[0]
            xs = self._gen_x_axis_with_offset(min(x), max(x))
            ys = functions.exp(*result[0])(xs)
            return xs, ys
        except RuntimeError:
            # Если вызывается исключение, то возвращаем исходные данные
            warn("Точки плохо подходят под апроксимацию экспоненйиальной функцией")
            return x, y

    def label(self, xvar='x', yvar='y'):
        try:
            return f'${yvar} = {format_monoid(round_to_n(self.koefs[0], 3), True)}' \
                   f'e^{{{round_to_n(self.koefs[1], 3)}{xvar}}} ' \
                   f'{format_monoid(round_to_n(self.koefs[2], 3))}$'
        except TypeError:
            return 'Экспонента, которая не смогла'


class Logarithmic(Approximator):
    """
    Логарифмический апроксиматор
    y = a * ln(bx + c) + d
    """

    def approximate(self, x, y):
        # пытаемся апроксимировать. если у scipy плохо получается, то оно выбрасывает ислючение RuntimeError
        try:
            result = scipy.optimize.curve_fit(functions.log_for_fit, x, y)
            self.meta = result
            self.koefs = self.meta[0]
            xs = self._gen_x_axis_with_offset(min(x), max(x))
            ys = functions.log(*result[0])(xs)

            return xs, ys

        except RuntimeError as e:
            # Если вызывается исключение, то возвращаем исходные данные
            warn("Точки плохо подходят под апроксимацию логирифмической функцией")
            return x, y

    def label(self, xvar='x', yvar='y'):

        try:

            return f'${format_monoid(round_to_n(self.koefs[0], 3), True)}\ln{{(' \
                   f'{format_monoid(round_to_n(self.koefs[1], 3), True)}x ' \
                   f'{format_monoid(round_to_n(self.koefs[2], 3))})}} ' \
                   f'{format_monoid(round_to_n(self.koefs[3], 3))}$'

        except IndexError:
            return 'Логарифм, который не смог'
