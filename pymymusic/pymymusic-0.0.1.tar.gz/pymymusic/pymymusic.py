from __future__ import unicode_literals
import time
import pyfiglet
from youtubesearchpython import VideosSearch
from youtubesearchpython import *
import json
import __future__
import youtube_dl

def pymymusic():
    result = pyfiglet.figlet_format("PYMYMUSIC")
    print(result)
    song = input("Enter the song name:")
    videosSearch = VideosSearch(song, limit = 1)
    data = json.dumps(videosSearch.result())
    data = json.loads(data)

    print(type(data['result']))
    for result in data['result']:
        link = (result['link'])

    url = link
    print(url)
    filename = f"{song}.mp3"
    ydl_opts = {
            'format':'bestaudio/best',
            'keepvideo':False,
            'outtmpl':filename,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print("Thankyou for Downloading the Video {}".format(filename))
    print('your file is saved in admin folder')

pymymusic()