from crostab import Crostab
from palett import fluo_matrix, fluo_vector
from palett.presets import FRESH, PLANET
from texting import AEU, ELLIP, liner
from veho.enum.matrix_directions import COLUMNWISE
from veho.matrix import size
from veho.vector import zipper

from pyspare.margin.crostab_margin import crostab_margin
from pyspare.padder.crostab_padder import crostab_padder


def deco_crostab(crostab: Crostab,
                 discrete=False,
                 read=None,
                 side_read=None,
                 head_read=None,
                 presets=(FRESH, PLANET),
                 direct=COLUMNWISE,
                 top=0,
                 bottom=0,
                 left=0,
                 right=0,
                 ansi=False,
                 full_angle=False,
                 level=0,
                 rule=ELLIP):
    height, width = size(crostab.rows)
    label_height, label_width = len(crostab.side), len(crostab.head)
    if not height or not width or not label_width or not label_height: return AEU
    crostab = crostab_margin(crostab, top, bottom, left, right, height, width, read, side_read, head_read, rule)
    # print(deco_vector(crostab.head))
    # print(deco_vector(crostab.side))
    # print(deco_matrix(crostab.rows))
    crostab = crostab_padder(crostab, ansi, full_angle)
    if presets:
        # vector_presets = (presets[0], presets[1])
        crostab = crostab.boot(
            side=fluo_vector(crostab.side, presets, mutate=True),
            head=fluo_vector(crostab.head, presets, mutate=True),
            rows=fluo_matrix(crostab.rows, direct, presets, mutate=True)
        )
    lines = [crostab.title + ' | ' + ' | '.join(crostab.head),
             '-+-'.join(crostab.rule)]
    lines.extend(zipper(crostab.side, crostab.rows,
                        lambda s, r: s + ' | ' + ' | '.join(r)))
    return liner(lines, level=level, discrete=discrete)
