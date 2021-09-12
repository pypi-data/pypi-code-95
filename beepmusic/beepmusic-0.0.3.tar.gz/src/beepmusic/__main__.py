#!/usr/bin/env python
#-*- utf-8 -*-
import beepmusic
from beepmusic import load_music
import argparse
import os, sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play BMC file')
    parser.add_argument('file', metavar='BMCFile', nargs='?', type=str,
                        help='BMCFile to play')
    parser.add_argument('--builtin', '-b', action="store_true",
                        help='play built-in music')
    parser.add_argument('--list', '-l', action="store_true",
                        help="list build-in melodies")

    args = parser.parse_args()

    moduleDir = os.path.dirname(beepmusic.__file__)
    if args.list:
        for file_ in os.listdir(os.path.join(moduleDir, "builtin_musics")):
            print(file_)
        exit()

    if args.builtin:
        player = load_music(os.path.join(moduleDir, "builtin_musics", args.file))
    else:
        player = load_music(args.file)
    player.play()
    exit()