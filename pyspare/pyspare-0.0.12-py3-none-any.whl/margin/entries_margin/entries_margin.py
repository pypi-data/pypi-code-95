from dataclasses import dataclass

from veho.entries.margin import margin_mapper, margin_mutate

from pyspare.margin.vector_margin import VectorMargin, sizing


@dataclass
class EntriesMargin(VectorMargin):
    # def __init__(self):
    #     VectorMargin.__init__(self,)

    @staticmethod
    def build(vec: list, head: int, tail: int) -> 'EntriesMargin':
        h, t = sizing(vec, head, tail)
        return EntriesMargin(vec, h, t)

    def map(self, kfn, vfn=None, mutate=False) -> 'EntriesMargin':
        boot, mapper = (self.reboot, margin_mutate) if mutate else (self.clone, margin_mapper)
        return boot(mapper(self.vec, kfn, vfn, self.head, self.tail))

    def stringify(self, kfn, vfn=None, mutate=False) -> 'EntriesMargin':
        kf = (lambda x: str(kfn(x))) if kfn else str
        vf = (lambda x: str(vfn(x))) if vfn else kf
        return self.map(kf, vf, mutate)
