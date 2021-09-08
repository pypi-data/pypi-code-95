from ject import oneself
from texting import ELLIP

from pyspare.margin import VectorMargin


def margin_set(vec, head, tail, read, hr=ELLIP):
    vn = VectorMargin.build(vec, head, tail)
    return (
        vn.map(oneself).to_list(hr),
        vn.stringify(read).to_list(hr)
    )
