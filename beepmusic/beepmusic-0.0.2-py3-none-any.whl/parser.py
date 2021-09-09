#-*- coding:utf-8 -*-
from typing import Union
from io import TextIOWrapper
from .beepmusic import MusicNotation, InvalidNotationError

class BMCParser(object):
    """
    A Light parser of BMC File. Can be treated as stylus in BeepPlayer.
    Example
        from beepmusic import BMCParser, BeepPlayer
        player = BeepPlayer()
        bmc = BMCParser("joy.bmc")
        player.tone_marker = bmc.tone_marker
        player.bpm = bmc.bpm
        player.load_stylus(bmc)
        player.play()
        player.close()
    """
    def __init__(self, file:Union[str, TextIOWrapper]):
        if type(file) == str:
            self.fstream = open(file, "rt", encoding="utf-8")
        else:
            self.fstream = file
        self.cur = None
        self.lineNum = 1
        self._more_notation = True
        self.process_head()
        self.advance()
    
    def process_head(self):
        # Name
        line = self.fstream.readline()
        self.name = line.split('=')[1].strip()

        # base pitch
        self.tone_marker = self.fstream.readline().strip()

        # timing
        line = self.fstream.readline()
        self.bpm = float(line.split('=')[1].strip())
    
    def parse_notation(self, notation:str):
        return MusicNotation(notation)

    def advance(self):
        while True:
            c = self.fstream.read(1)
            # 处理结束
            if c == '':
                self._more_notation = False
                break
            # 读到空格或\t或换行或|则跳过
            if c in " \t\n\r|":
                if c == '\n':
                    self.lineNum += 1
            # 处理注释
            elif c == '%':
                self.fstream.readline()
                self.lineNum += 1
            # 处理正常音符
            elif c in "<>#b1234567-":
                self.fstream.seek(self.fstream.tell() - 1)
                self.parse_notation()
                break
            elif c == "[":
                self.fstream.seek(self.fstream.tell() - 1)
                self.parse_complex_notation()
                break
            else:
                raise SyntaxError(f"In line {self.lineNum}: Unrecognized token {c}")
    
    def _parse_single_notation(self):
        tokens = []
        while True:
            c = self.fstream.read(1)
            if c in "<>":
                tokens.append(c)
            elif c in "#b":
                if len(tokens) > 0 and tokens[-1] in "#b":
                    raise SyntaxError(f"In line {self.lineNum}: Too many rising/falling notations")
                tokens.append(c)
            elif c in "1234567-":
                tokens.append(c)
                break
            else:
                raise SyntaxError(f"In line {self.lineNum}: Unexpected end of a notation")
        return ''.join(tokens)
    
    def parse_notation(self):
        self.cur = MusicNotation().parse_notation(self._parse_single_notation())

    def parse_complex_notation(self):
        tokens = []
        self.fstream.read(1)
        while True:
            c = self.fstream.read(1)
            if c == ']':
                break
            elif c == '\n':
                raise SyntaxError(f"In line {self.lineNum}: Unexpected end of a notation")
            else:
                tokens.append(c)
        try:
            self.cur = MusicNotation().parse_notation(''.join(tokens))
        except InvalidNotationError as e:
            raise SyntaxError(f"In line {self.lineNum}: {e.args[0]}")

    def has_more_notations(self) -> bool:
        return self._more_notation

    def close(self):
        self.fstream.close()

    def __iter__(self):
        self.cur = None
        self.lineNum = 1
        self._more_notation = True
        self.fstream.seek(0)
        self.process_head()
        self.advance()
        return self
    
    def __next__(self):
        if not self.has_more_notations():
            raise StopIteration
        cur = self.cur
        self.advance()
        return cur
        