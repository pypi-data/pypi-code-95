#!/usr/bin/env python
#-*- utf-8 -*-
from beepmusic import load_music
import sys

if __name__ == "__main__":
    player = load_music(sys.argv[1])
    player.play()