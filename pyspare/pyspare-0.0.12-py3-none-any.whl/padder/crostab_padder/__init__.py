from crostab import Crostab, Series
from texting import SP

from pyspare.padder.series_padder import series_padder
from pyspare.padder.table_padder import table_padder


def crostab_padder(crostab: Crostab, ansi=False, full_angle=False, fill=SP):
    series = Series(points=crostab.side, title=crostab.title)
    side_part = series_padder(series, ansi, full_angle)
    body_part = table_padder(crostab, ansi, full_angle)
    return Crostab(
        side=side_part.points,
        head=body_part.head,
        rows=body_part.rows,
        title=side_part.title,
        rule=[side_part.rule] + body_part.rule
    )
