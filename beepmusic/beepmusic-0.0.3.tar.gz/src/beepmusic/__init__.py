#-*- coding:utf-8 -*-
from .beepmusic import BeepPlayer
from .parser import BMCParser

def load_music(fname:str) -> BeepPlayer:
    """
    Load BMC file to a new player.
    """
    bmcParser = BMCParser(fname)
    player = BeepPlayer(tone_marker=bmcParser.tone_marker, bpm=bmcParser.bpm)
    player.load_stylus(bmcParser)
    return player
