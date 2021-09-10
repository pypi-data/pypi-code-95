from math import log10, floor

from ..config import round_to


def round_to_n(x, n):
    """
    Округляет до n значащих цифр
    :param x: число
    :param n: кол-во значащих цифр
    :return:
    """
    return round(x, -int(floor(log10(abs(x))) - n + round_to - 2))


def get_sign(x):
    """
    Возвращает знак числа
    :param x: число
    :return: "+" если x > 0, иначе "-"
    """
    return "+" if x >= 0 else "-"


def format_monoid(koef, first=False):
    """
    Форматирует число в хороший вид
    :param koef: коэффициент
    :param first: оставлять ли знак плюс
    :return: форматированный коэффициент в латех
    """

    s = str(abs(round_to_n(koef, 3)))

    # Форматирование больших по модулю степеней (числа с e в середине)
    if 'e' in s:
        t = s.split('e')
        s = f'{t[0]}*10^{{{int(t[1])}}}'

    # Форматирование знака
    sign = get_sign(koef)

    if first and koef > 0:
        sign = ""

    return f'{sign}{s}'
