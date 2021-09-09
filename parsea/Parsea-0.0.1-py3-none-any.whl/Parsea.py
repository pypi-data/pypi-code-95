import re
from typing import Iterable, Union


class Parsea:
    """
    Scannerless Parser with Regex support
    
    Example:
    ```py
    from Parsea import Parsea

    class Parser(Parsea):
        
        def parseInt(self, string: str):
            self.init(string)
            num = self.while_strings("0123456789")
            return int(num) if num else None
        
        def parseAlpha(self, string: str):
            self.init(string)
            alpha = self.while_strings(self.in_range("a","z")+self.in_range("A","Z"))
            return alpha if alpha else None

    p = Parser()

    print(p.parseInt('1203')) # 1203
    print(p.parseInt('heLLo')) # None

    print(p.parseAlpha('heLLo')) # heLLo
    print(p.parseAlpha('1203')) # None
    ```
    """
    def __init__(self) -> None:
        self.ignore = lambda c: c is not None and c.isspace()
        self.do_ignore = True

    def init(self, string: str):
        self._re_cache = {}
        self.source, self.len_s = string, len(string)
        self.pos, self.char = -1, None
        self.old_pos = -1
        self.advance()

    def advance(self, step: int = 1):
        c = ""
        self.old_pos = self.pos
        for _ in range(step):
            self.pos += 1
            c += self.char or ""
            self.char = None if self.pos >= self.len_s else self.source[self.pos]
            if self.char is None:
                break
        return c

    def advance_until(self, lamb):
        c = ""
        while lamb(self.char):
            c += self.advance()
        return c

    def peek(self, step: int = 1):
        p = self.pos+step
        return "" if p >= self.len_s else self.source

    def undo(self, step: int = 1):
        c = ""
        self.old_pos = self.pos
        for _ in range(step):
            self.pos -= 1
            c += self.char or ""
            self.char = None if self.pos < 0 else self.source[self.pos]
            if self.char is None:
                break
        return c[::-1]

    def slice_s(self, end: int = -1, start: int = 0):
        r_pos = start+self.pos
        return self.source[r_pos:r_pos+end]

    def check_ignore(self):
        return self.advance_until(self.ignore) if self.do_ignore else ""

    def match_str(self, string: str, start: int = 0):
        self.check_ignore()
        return self.slice_s(end=len(string), start=start) == string

    def match_re(self, pattern: str, start: int = 0) -> Union[re.Match, bool]:
        self.check_ignore()
        if pattern not in self._re_cache:
            self._re_cache[pattern] = re.compile(pattern)
        return self._re_cache[pattern].match(self.source, self.pos+start) or False

    def maybe_str(self, string: str):
        self.check_ignore()
        if not self.match_str(string):
            return False
        return self.advance(step=len(string))

    def maybe_re(self, pattern: str, raw: bool=True):
        self.check_ignore()
        m = self.match_re(pattern)
        if m:
            text = self.advance(m.end()-self.pos)
            return text if raw is True else m
        return False
    
    def in_range(self, char1: str, char2: str):
        if not (char1 and char2):
            return ()
        o_c1, o_c2 = ord(char1[0]), ord(char2[0])
        
        # This code is not too bad:
        return tuple((chr(i) for i in \
            range(*( (o_c1, o_c2) if o_c2 > o_c1 else (o_c2, o_c1) ))))
    
    def while_strings(self, iter__: Iterable):
        c = ""
        while self.char is not None and self.char in iter__:
            c += self.advance()
        return c
    
    def optional(self, func, *args):
        for i, a in enumerate(args):
            m = func(a)
            if m:
                return i, m
        return -1, None