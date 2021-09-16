import click
from pytube import YouTube
from tqdm import tqdm
import time


@click.command()
@click.option('--video', '-v', help='Input Youtube link', required=True)
def cli(video):
    """Phyra Youtube downloader"""
    path = input('Input File Destination : ')
    yt_video = YouTube(video)
    print('======== VIDEO INFO ========')
    print(f"- Title : {yt_video.title}")
    print(f'- Thubnail : {yt_video.thumbnail_url}')
    print('============================')
    confirmation = input('Are you sure to download the video? [y/N] ')
    if confirmation == 'y':
        yt_video.streams.filter(file_extension = "mp4").get_highest_resolution().download(path)
        for i in tqdm (range (100), 
                   desc="Downloading...", 
                   ascii=False, ncols=75):
            time.sleep(0.01)
        print(f'Downloaded! Your video on {path}')
        print('')
        print('')
    else:
        print('Aborted!')
