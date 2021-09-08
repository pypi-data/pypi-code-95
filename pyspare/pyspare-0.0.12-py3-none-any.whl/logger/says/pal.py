from texting import SP, parenth, LF, bracket
from veho.vector import mutate


def tab(ind): return SP * (ind << 1)


class Pal:
    name: str = ''
    des: str = ''
    ind: int = 0

    def __init__(self, name):
        self.name = name

    def p(self, words):
        self.des += SP + words
        return self

    def br(self, words):
        self.des += SP + parenth(words)
        return self

    def to(self, someone):
        someone = someone.name if isinstance(someone, Pal) else str(someone)
        self.des += ' -> ' + bracket(someone)
        return self

    def __call__(self, *args, sep=SP, end=LF, file=None):
        signature = bracket(self.name)
        if self.ind: signature = tab(self.ind) + signature
        if self.des:
            signature += self.des
            self.des = ''
        if len(args) and (LF in str(args[0])) and (args := list(args)):
            mutate(args, lambda text: (LF + str(text)).replace(LF, LF + tab(self.ind + 1)))
        print(signature, *args, sep=sep, end=end, file=file)

    @property
    def asc(self):
        self.ind += 1
        return self

    @property
    def desc(self):
        if self.ind: self.ind -= 1
        return self
