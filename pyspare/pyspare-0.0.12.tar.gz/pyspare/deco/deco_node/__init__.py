import inspect

from intype import is_numeric
from palett import fluo_entries, fluo_vector
from texting import brace, bracket, parenth
from veho.entries import mutate_values
from veho.vector import mutate

from pyspare.deco.deco_node.helpers import mutate_key_pad
from pyspare.deco.deco_node.preset import DecoPreset
from pyspare.deco.deco_node.render import render_entries, render_vector


def deco(ob): return deco_node(DecoPreset(), ob, 0)


def deco_node(self, node, level=0, indent=0):
    if node is None: return str(node)
    if isinstance(node, str): return node if is_numeric(node) else str(node)
    if isinstance(node, (int, float)): return node
    if isinstance(node, bool): return node
    if isinstance(node, complex): return str(node)
    if isinstance(node, list): return '[list]' if level >= self.depth else bracket(de_ve(self, node[:], level))
    if isinstance(node, dict): return '[dict]' if level >= self.depth else brace(de_en(self, list(node.items()), level))
    if isinstance(node, tuple): return '[tuple]' if level >= self.depth else parenth(de_ve(self, list(node[:]), level))
    if inspect.isfunction(node): return str(node)
    if inspect.isclass(type(node)): return de_ob(self, node, level)
    return str(node)


def de_ve(self, vector, lv):
    mutate(vector, lambda v: str(deco_node(self, v, lv + 1)))
    if self.presets: fluo_vector(vector, self.presets, mutate=True)
    return render_vector(self, vector, lv)


def de_en(self, entries, lv):
    if not len(entries): return ''
    key_wd = mutate_key_pad(entries)
    mutate_values(entries, lambda v: str(deco_node(self, v, lv + 1, key_wd)))
    if self.presets: fluo_entries(entries, self.presets, mutate=True)
    return render_entries(self, entries, lv)


def de_ob(self, ob, lv):
    abstract = ob.__dict__ \
        if hasattr(ob, '__dict__') \
        else {s: getattr(ob, s) for s in ob.__slots__} \
        if hasattr(ob, '__slots__') \
        else str(ob)
    return f'[{type(ob).__name__}] {deco_node(self, abstract, lv)}'
