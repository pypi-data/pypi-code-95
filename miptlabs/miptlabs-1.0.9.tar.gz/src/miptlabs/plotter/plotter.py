import matplotlib.pyplot as plt
from matplotlib.figure import Figure


class NothingDrawError(Exception):
    def __init__(self, text):
        self.txt = text


class LEGEND_FROM_APPROXIMATOR:
    ...


def _make_tuples_from_none(*tuples, length=1):
    """
    Делает из None кортеж длиной length, если передан не None, то оставляет его, как есть
    """
    result = []
    for tuple_ in tuples:
        if tuple_ is None:
            result.append(tuple([None] * length))

        else:
            result.append(tuple_)

    return result


def _set_ticks_fontsize(axes, xfontsize, yfontsize):
    """
    Устанавливает размер шрифта подписям по осям
    :param axes: объект графика
    :param xfontsize: размер шрифта по оси x
    :param yfontsize: размер шрифта по оси y
    :return: None
    """
    for item in axes.get_xticklabels():
        item.set_fontsize(xfontsize)

    for item in axes.get_yticklabels():
        item.set_fontsize(yfontsize)


def _get_default_params():
    """
    Генерирует значения размеров шрифта по умолчанию
    :return:
    """
    params = dict()

    params['figsize'] = (10, 8)
    params['dpi'] = 100

    params['legend_loc'] = 'best'

    params['xticks_fontsize'] = 16
    params['yticks_fontsize'] = 16
    params['xlabel_fontsize'] = 22
    params['ylabel_fontsize'] = 22
    params['legend_fontsize'] = 20
    params['title_fontsize'] = 26

    return params


def _update_params(params, kwargs):
    """
    Обновляет значения параметров построения графика с учётом переданных дополнитеьных параметров
    :param params:
    :param kwargs:
    :return:
    """

    targets = ('figsize', 'dpi', 'legend_loc',
               'xticks_fontsize', 'yticks_fontsize',
               'xlabel_fontsize', 'ylabel_fontsize',
               'legend_fontsize', 'title_fontsize',
               'LEGEND_FROM_APPROXIMATOR', 'xvar', 'yvar')

    for target in targets:
        if target in kwargs:
            params[target] = kwargs.pop(target)

    if kwargs:
        print(f'Лишние аргументы', kwargs)


def _get_default_color(i=0):
    """
    :return: первый цвет в цикле цветов matplotlib, точнее тускло-синий
    """
    return plt.rcParams['axes.prop_cycle'].by_key()['color'][i % 10]


def _enable_minor_ticks(axes):
    """
    Включает побочную сетку на графике
    :param axes:
    :return:
    """
    axes.minorticks_on()
    axes.grid(which='major', color='k', linewidth=0.8)
    axes.grid(which='minor', color='k', linestyle=':')


def _set_font_params(axes, params, xlabel, ylabel, title):
    # Устанавливает размер шрифта для подписей по осям
    _set_ticks_fontsize(axes, params['xticks_fontsize'], params['yticks_fontsize'])

    # Устанавливает размер шрифта для разных элементов
    axes.set_xlabel(xlabel, fontsize=params['xlabel_fontsize'])
    axes.set_ylabel(ylabel, fontsize=params['ylabel_fontsize'])
    axes.set_title(title, fontsize=params['title_fontsize'])


def _get_axes(axes, params, minot_ticks):
    """
    Создаёт новые объект графика и фигуры, если axes=None
    Возвращает текущие оси, если они не None
    """
    if axes is None:
        figure, axes = plt.subplots(figsize=params['figsize'], dpi=params['dpi'])
        if minot_ticks:
            _enable_minor_ticks(axes)

    return axes


def _prepare(axes, xlabel, ylabel, title, minor_ticks, points, line, xerr, yerr, approximator, kwargs):
    _check_correct_input(points, line, xerr, yerr, approximator)

    # Инициализирует параметры
    params = _get_default_params()

    # Обновляет параметры
    _update_params(params, kwargs)

    # Создаёт новые объект графика и фигуры, если не переданы существующие
    axes = _get_axes(axes, params, minor_ticks)

    # ----------------Шрифты----------------
    _set_font_params(axes, params, xlabel, ylabel, title)

    return axes, params


def _check_correct_input(points, line, xerr, yerr, approximator):
    """
    Проверяет, может ли что-то нарисоваться.
    Если нет, то выбрасывает исключение NothingDrawError
    :param points:
    :param line:
    :param xerr:
    :param yerr:
    :return:
    """
    if not points and not line and not xerr and not yerr and not approximator:
        raise NothingDrawError("Хотя бы один из параметров points, line, xerr, yerr должен быть True,"
                               " чтобы что-то нарисовалось")


def _draw(axes, x, y, xerr, yerr, color, legend, points, line, approximator, params):
    """
    Сама функция рисования
    """
    # Устанавливает стандартный цвет, если не передан другой
    if color is None:
        color = _get_default_color()

    # Нужно для костыля, чтобы легенда отрисовыволась лишь один раз
    label = legend

    if approximator:
        x_, y_ = approximator.approximate(x, y)

        if params.get("LEGEND_FROM_APPROXIMATOR"):
            xvar = 'x'
            yvar = 'y'

            if 'xvar' in params:
                xvar = params['xvar']
            if 'yvar' in params:
                yvar = params['yvar']

            app_label = approximator.label(xvar, yvar)
        else:
            app_label = None

        axes.plot(x_, y_, c=color, label=app_label)

    # Рисует точки, если нужно
    if points:
        axes.scatter(x, y, c=color, label=label)
        label = None

    # Рисует кресты погрешностей, если нужно
    if xerr or yerr:
        axes.errorbar(x, y, fmt='none', xerr=xerr, yerr=yerr, c=color, label=label)
        label = None

    # Соединяет точки ломаной, если нужно
    if line:
        axes.plot(x, y, c=color, label=label)
        label = None

    return axes


def show_recommendations():
    ...

def pretty_plot(x, y, xerr=None, yerr=None,
                xlabel=None, ylabel=None, title=None, legend=None,
                minor_ticks=True, color=None, points=True, line=False,
                axes=None, approximator=None, **kwargs):
    """
    Рисует график, с требованиями лабников.
    По умолчания не соединяет точки
    TODO: пока не умеет выносить степень. в будущем это появится.
    TODO: может поменяться интерфейс
    для отображения можно искользовать:
    matplotlib.pyplot.show(), или pretty_plot(...).figure.show(), или show(), определнный ниже
    для сохранения можно использовать:
    matplotlib.pyplot.savefig(filename), или pretty_plot(...).figure.savefig(filename), или savefig(fig, filename), определнный ниже
    :param x: координаты по оси x
    :param y: координаты по оси y
    :param xerr: погрешности по оси x. Либо одно число (применится к все точкам), либо список (применится к соответсвующей точке).
    :param yerr: погрешности по оси y. Либо одно число (применится к все точкам), либо список (применится к соответсвующей точке).
    :param xlabel: подпись по оси x
    :param ylabel: подпись по оси y
    :param title: название графика
    :param legend: легенда
    :param minor_ticks: нужна ли впсомогательная сетка
    :param color: цвет графика. Если None, то будет синий
    :param points: нужно ли рисвоать точки
    :param line: нужно ли соединить ломаной все точки
    :param axes: объект графика. Можно ппередать, чтобы дорисовать всё на существующем графике
    :param approximator: аппроксиматор для точек, должен быть экземпляром класса Approximator
    :param kwargs: дополнительные агрменты:
    :Keyword Arguments:
    * *figsize* (``tuple[int]``) --
      размер графика в дюймах, по умолчанию 10 на 8
    * *dpi* (``int``) --
      количество пикселей на дюйм, по умолчанию 100
    * *legend_loc* (``str``) --
      положение легенды (см. документацию matplotlib), по умолчанию best
    * *xticks_fontsize* (``int``) --
      размер шрифта подписей оси x, по умолчанию 16
    * *yticks_fontsize* (``int``) --
      размер шрифта подписей оси y, по умолчанию 16
    * *xlabel_fontsize* (``int``) --
      размер шрифта обозначения оси x, по умолчанию 22
    * *ylabel_fontsize* (``int``) --
      размер шрифта обозначения оси y, по умолчанию 22
    * *title_fontsize* (``int``) --
      размер шрифта заголовка, по умолчанию 26
    * *legend_fontsize* (``int``) --
      размер шрифта легенды, по умолчанию 22
    * *LEGEND_FROM_APPROXIMATOR* (``int``) --
      если передано True, то рисует легенду ещё из аппроксиматора
    * *xvar* (``str``) --
      величина по оси x, если легенда рисуется из аппроксиматора
    * *yvar* (``str``) --
      величина по оси y, если легенда рисуется из аппроксиматора
    :return: объект только что нарисованного графика
    """

    # ----------------Инициализация----------------
    axes, params = _prepare(
        axes=axes,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        minor_ticks=minor_ticks,
        points=points,
        line=line,
        xerr=xerr,
        yerr=yerr,
        approximator=approximator,
        kwargs=kwargs
    )

    # ----------------Рисование----------------
    _draw(axes, x, y, xerr, yerr, color, legend, points, line, approximator, params)

    # Рисует легенду, если нужно
    if legend or params.get("LEGEND_FROM_APPROXIMATOR"):
        axes.legend(loc=params['legend_loc'], fontsize=params['legend_fontsize'])

    return axes


def pretty_plot_many(xs, ys, xerrs=None, yerrs=None,
                     xlabel=None, ylabel=None, title=None, legends=None,
                     minor_ticks=True, colors=None, points=True, line=False,
                     axes=None, approximator=None, **kwargs):
    r"""
    :param xs: наборы координат по оси x
    :param ys: наборы координат по оси y
    :param xerrs: наборы погрешностей по оси x.
    Либо одно число (применится к все точкам), либо список (применится к соответсвующей точке).
    :param yerrs: наборы погрешностей по оси y.
    Либо одно число (применится к все точкам), либо список (применится к соответсвующей точке).
    :param xlabel: наборы подписей по оси x
    :param ylabel: наборы подписей по оси y
    :param title: название графика
    :param legends: легенды
    :param minor_ticks: нужна ли впсомогательная сетка
    :param colors: наборы цветов графика. Если None, то будет синий
    :param points: нужно ли рисвоать точки
    :param line: нужно ли соединить ломаной все точки
    :param axes: объект графика. Можно передать, чтобы дорисовать всё на существующем графике
    :param approximator: аппроксиматор для точек, должен быть экземпляром класса Approximator
    :param kwargs: дополнительные агрменты:
    :Keyword Arguments:
    * *figsize* (``tuple[int]``) --
      размер графика в дюймах, по умолчанию 10 на 8
    * *dpi* (``int``) --
      количество пикселей на дюйм, по умолчанию 100
    * *legend_loc* (``str``) --
      положение легенды (см. документацию matplotlib), по умолчанию best
    * *xticks_fontsize* (``int``) --
      размер шрифта подписей оси x, по умолчанию 16
    * *yticks_fontsize* (``int``) --
      размер шрифта подписей оси y, по умолчанию 16
    * *xlabel_fontsize* (``int``) --
      размер шрифта обозначения оси x, по умолчанию 22
    * *ylabel_fontsize* (``int``) --
      размер шрифта обозначения оси y, по умолчанию 22
    * *title_fontsize* (``int``) --
      размер шрифта заголовка, по умолчанию 26
    * *legend_fontsize* (``int``) --
      размер шрифта легенды, по умолчанию 22
    * *LEGEND_FROM_APPROXIMATOR* (``bool``) --
      если передано True, то рисует легенду ещё из аппроксиматора
    * *xvar* (``str``) --
      величина по оси x, если легенда рисуется из аппроксиматора
    * *yvar* (``str``) --
      величина по оси y, если легенда рисуется из аппроксиматора
    :return: объект только что нарисованного графика
    """

    # ----------------Инициализация----------------
    axes, params = _prepare(
        axes=axes,
        xlabel=xlabel,
        ylabel=ylabel,
        title=title,
        minor_ticks=minor_ticks,
        points=points,
        line=line,
        xerr=xerrs,
        yerr=yerrs,
        approximator=approximator,
        kwargs=kwargs
    )

    # Создаём кортежы из None длины = количеству графиков
    legends, colors, xerrs, yerrs = _make_tuples_from_none(legends, colors, xerrs, yerrs)

    # ----------------Рисование----------------
    for num, (x, y, xerr, yerr, legend, color) in enumerate(zip(xs, ys, xerrs, yerrs, legends, colors)):
        _draw(axes, x, y, xerr, yerr, color, legend, points, line, approximator, params)

    # Рисует легенду, если нужно
    if legends or params.get("LEGEND_FROM_APPROXIMATOR"):
        axes.legend(loc=params['legend_loc'], fontsize=params['legend_fontsize'])

    return axes


def show(*args, **kwargs):
    """
    Рисует все сгенерированные графики. По-сути обертка над matplotlib.pyplot.show
    :param args:
    :param kwargs:
    :return:
    """
    return plt.show(*args, **kwargs)


def savefig(obj, filename, *, transparent=None, **kwargs):
    """
    Сохраняет фигуру. По-сути обертка над встроенной функцие сохранения
    :param obj:
    :param filename:
    :param transparent:
    :param kwargs:
    :return:
    """
    figure = obj if isinstance(obj, Figure) else obj.figure

    figure.savefig(filename, transparent=transparent, **kwargs)
