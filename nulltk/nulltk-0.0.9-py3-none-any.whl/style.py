import tkinter as tk
from . import colors
from .color import Color

from dataclasses import dataclass

@dataclass
class Style:
    # Defaults from atelierdune.dark:
    # https://terminal.sexy/#ICAdpqKMICAd1zc3YKw5z7AXZoThuFTUH62DpqKMfXpo1zc3YKw5z7AXZoThuFTUH62D_vvs
    background:                Color = Color.from_hex('#20201d')
    foreground:                Color = Color.from_hex('#a6a28c')
    backgroundActive:        Color = background.lighter(0.1)
    foregroundActive:        Color = Color.from_hex('#7d7a68')
    interactive:            Color = Color.from_hex('#60ac39')
    borderWidth:            int = 0
    highlightBorderWidth:    int = 0
    relief:                    str = tk.FLAT
    # font -> Droid Sans Mono 14?

    def apply(self, root):
        root.option_add("*background", self.background.as_hex())
        root.option_add("*foreground", self.foreground.as_hex())
        root.option_add("*activeBackground", self.backgroundActive.as_hex())
        root.option_add("*activeForeground", self.foregroundActive.as_hex())
        root.option_add("*insertBackground", self.foreground.as_hex())
        root.option_add("*interactive", self.interactive.as_hex())
        root.option_add("*borderWidth", self.borderWidth)
        root.option_add("*highlightThickness", self.highlightBorderWidth)
        # Canvas defaulting to non-zero
