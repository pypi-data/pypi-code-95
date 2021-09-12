#-*- coding:utf-8 -*-
from typing import Iterable
from winsound import Beep
from .musicLaw import AbsoluteFreqMap, RelativeFreqMap
import time


class InvalidNotationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FreqOutRangeError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Pitch(object):
    def __init__(self, base_pitch: str, level: int):
        self.base_pitch = base_pitch
        self.level = level
    
    def __str__(self) -> str:
        return f"Pitch(base={self.base_pitch}, level={self.level})"
    
    def __repr__(self) -> str:
        return self.__str__()

class MusicNotation(object):
    def __init__(self):
        self.notation = None
        self.pitch = None
        self.duration = None

    def parse_notation(self, notation: str):
        fullNotations = [s.strip() for s in notation.split(',')]
        if len(fullNotations) == 1:
            pitch = fullNotations[0]
            duration = 1.
        elif len(fullNotations) == 2:
            pitch = fullNotations[0]
            try:
                duration = float(fullNotations[1])
            except ValueError:
                raise InvalidNotationError(f"Unrecognized notation {notation}")

        # Parse Pitch
        level = 0
        for index, c in enumerate(pitch):
            if c == '<':
                level -= 1
            elif c == '>':
                level += 1
            else:
                break
        base_pitch = pitch[index:]

        # duration need no parsing
        self.pitch = Pitch(base_pitch, level)
        self.duration = duration
        return self

    def isPause(self) -> bool:
        return self.pitch.base_pitch == '-'
    
    def __str__(self) -> str:
        return f"Notation({str(self.pitch)}, dur={self.duration})"

    def __repr__(self) -> str:
        return self.__str__()

class BeepPlayer(object):
    """
    Player using system Beep function.
    Play beep music with specific tone and speed parameters.
    Example
        player = BeepPlayer(base_freq=261, time=700)
        player.load_stylus(stylus)
        player.play()
    Notes
        base_freq and tone_marker, time and bpm, you only need to specify one parameter
        in these pairs. And the modification of one parameter will cause the automatic
        modification of the other parameter
    """
    def __init__(self,
                 base_freq: int = None,
                 tone_marker: str = None,
                 time: int = None,
                 bpm: float = None):
        """
        Arguments
            base_freq: The frequency of 'do'(or, '1' notation).
            tone_marker: Tone marker. Takes the format of '[notation]=[absolute-notation]',
                like '1=C', '2=E', '<#4=C'
            time: Time of duration=1, in miliseconds
            bpm: beats per minute.
        """
        self.stylus = None
        self.tick = None
        self.loc = 0

        self.__base_freq = None
        self.__tone_marker = None
        self.__time = None
        self.__bpm = None
        
        if base_freq != None:
            self.base_freq = base_freq
        elif tone_marker != None:
            self.tone_marker = tone_marker
        else:
            self.tone_marker = "1=C"
        if time != None:
            self.time = time
        elif bpm != None:
            self.bpm = bpm
        else:
            self.bpm = 60
    
    def load_stylus(self, stylus:Iterable):
        """
        Arguments
            stylus: Iterable[MusicNotaion]
        Notes
            Some iterable objects in python can't iterate twice.
            For these objects, self.reset() method won't work.
        """
        self.stylus = stylus
        self.tick = iter(stylus)
        self.loc = 0
    
    @property
    def base_freq(self):
        return self.__base_freq
    
    @base_freq.setter
    def base_freq(self, base_freq:int):
        self.tone_marker = None
        self.base_freq = base_freq
    
    @property
    def tone_marker(self):
        return self.__tone_marker
    
    @tone_marker.setter
    def tone_marker(self, tone_marker:str):
        rela, abso = [s.strip() for s in tone_marker.split('=')]
        try:
            absoFreq = AbsoluteFreqMap[abso]
        except KeyError:
            raise InvalidNotationError(f"Unrecognized Absolute Notation: {abso}")
        relaNotation = MusicNotation().parse_notation(rela)
        try:
            relaFreq = 2 ** (RelativeFreqMap[relaNotation.pitch.base_pitch] + relaNotation.pitch.level)
        except KeyError:
            raise InvalidNotationError(f"Unrecognized Relative Notation: {rela}")
        self.__base_freq = absoFreq / relaFreq
        self.__tone_marker = tone_marker

    @property
    def time(self):
        return self.__time

    @time.setter
    def time(self, time: int):
        self.__time = time
        self.__bpm = self.time_to_bpm(time)

    @property
    def bpm(self):
        return self.__bpm
    
    @bpm.setter
    def bpm(self, bpm: float):
        self.__bpm = bpm
        self.__time = self.bpm_to_time(bpm)

    def play(self, num: int = None) -> None:
        """
        Play beep music.
        Arguments:
            num: How many notations to play.
                If not specified, all notations will be played.
        """
        if num == None:
            for notation in self.tick:
                try:
                    self.play_notation(notation)
                except Exception as e:
                    raise type(e)(f"loc {self.loc}", *e.args)
                self.loc += 1
        else:
            for _, notation in zip(range(num), self.tick):
                try:
                    self.play_notation(notation)
                except Exception as e:
                    raise type(e)(f"loc {self.loc}", *e.args)
                self.loc += 1

    def reset(self) -> None:
        """
        Reset the stylus to the beginning.
        Notes
            Some iterable objects in python can't iterate twice.
            For these objects, self.reset() method won't work.
        """
        self.tick = iter(self.stylus)
        self.loc = 0

    def play_notation(self, notation: MusicNotation) -> None:
        duration = int(notation.duration * self.time)
        if notation.isPause():
            time.sleep(duration/1000)
            return
        try:
            baseLogFreq = RelativeFreqMap[notation.pitch.base_pitch]
        except KeyError:
            raise InvalidNotationError(
                f"Unrecognized notation {notation.notation}")
        LogFreq = baseLogFreq + notation.pitch.level
        freq = int(self.base_freq * 2**LogFreq)
        if freq < 37:
            raise FreqOutRangeError(
                f"pitch {notation.notation} is too low: {freq} Hz")
        if freq > 32767:
            raise FreqOutRangeError(
                f"pitch {notation.notation} is too high: {freq} Hz")
        Beep(freq, duration)

    @classmethod
    def bpm_to_time(cls, bpm: float) -> int:
        return int(60000 / bpm)

    @classmethod
    def time_to_bpm(cls, time: int) -> float:
        return 60000 / time
