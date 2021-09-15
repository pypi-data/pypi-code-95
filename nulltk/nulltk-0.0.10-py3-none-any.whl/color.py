class Color:
    def __init__(self, r = 0, g = 0, b = 0):
        self.r, self.g, self.b = r, g, b

    def lighten(self, factor = 0.5):
        lerp = lambda x: x + (255-x)*factor
        self.set_rgb(*map(lerp, self.rgb))
        return self

    def darken(self, factor = 0.5):
        #self.set_hsv(self.h, self.s, self.v + (0.0-self.v)*factor)
        lerp = lambda x: x + (0-x)*factor
        self.set_rgb(*map(lerp, self.rgb))
        return self

    def lighter(self, factor = 0.5):
        return self.clone().lighten(factor)

    def darker(self, factor = 0.5):
        return self.clone().darken(factor)

    def clone(self): return Color(self.r, self.g, self.b)

    def set_rgb(self, r, g, b):
        self.r, self.g, self.b = r, g, b

    def set_hsv(self, h, s, v):
        c = v*s
        x = c*(1 - abs(((h/60) % 2) - 1))
        m = v - c

        if       0 <= h <= 60:  r1, g1, b1 = (c, x, 0)
        elif  60 <= h <= 120: r1, g1, b1 = (x, c, 0)
        elif 120 <= h <= 180: r1, g1, b1 = (0, c, x)
        elif 180 <= h <= 240: r1, g1, b1 = (0, x, c)
        elif 240 <= h <= 300: r1, g1, b1 = (x, 0, c)
        elif 300 <= h <= 360: r1, g1, b1 = (c, 0, x)

        self.r, self.g, self.b = map(lambda k: (k+m)*255, (r1, g1, b1))
        return self

    def as_hex(self):
        return f'#{int(self.r):02x}{int(self.g):02x}{int(self.b):02x}'

    @property
    def hex(self): return self.as_hex()

    @classmethod
    def from_hex(self, hexstring: str):
        hexstring = hexstring.replace('#','')
        if len(hexstring) != 6:
            raise Exception(f"Tried to get color from hex string of invalid length: '{hexstring}'")
        return Color(*[int(hexstring[i : i+2], 16) for i in range(0, len(hexstring), 2)])

    @classmethod
    def from_hsv(self, h, s, v):
        return Color().set_hsv(h, s, v)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def hsv(self):
        r1 = self.r/255
        g1 = self.g/255
        b1 = self.b/255

        cmax = max(r1,g1,b1)
        cmin = min(r1,g1,b1)

        delta = cmax - cmin
        if     delta == 0: hue = 0
        elif cmax == r1: hue = 60 * (((g1-b1)/delta) % 6)
        elif cmax == g1: hue = 60 * (((g1-b1)/delta) + 2)
        elif cmax == b1: hue = 60 * (((g1-b1)/delta) + 2)

        if cmax == 0:    sat = 0
        else:            sat = delta/cmax

        val = cmax
        return (hue, sat, val)

    @property
    def hue(self): return self.hsv[0]
    @property
    def saturation(self): return self.hsv[1]
    @property
    def value(self): return self.hsv[2]
    @property
    def h(self): return self.hue
    @property
    def s(self): return self.saturation
    @property
    def v(self): return self.value

    def __eq__(self, o):
        return self.r == o.r and self.g == o.g and self.b == o.b

    def __repr__(self):
        return f"({self.r:0.2f},{self.g:0.2f},{self.b:0.2f})"

