from __future__ import unicode_literals
import youtube_dl
import youtube_dl.utils
import requests
import re
from PIL import Image
from io import BytesIO
import tempfile
from pathlib import Path

class BasketCase:
    def __init__(self, session_id):
        self._cookies = {'sessionid': session_id}
        self._output_videos = str(Path.cwd()) + '/basketcase/videos'
        self._output_images = str(Path.cwd()) + '/basketcase/images'
        
        Path(self._output_videos).mkdir(parents=True, exist_ok=True)
        Path(self._output_images).mkdir(parents=True, exist_ok=True)

    def fetch(self, urls):
        for url in urls:
            print('Fetching:', url)

            request = requests.get(url, cookies=self._cookies)
            image_urls = re.findall(r'"display_url":"(.*?)"', request.text)
            video_urls = re.findall(r'"video_url":"(.*?)"', request.text)

            for image_url in image_urls:
                self._get_image(image_url)

            for video_url in video_urls:
                self._get_video(video_url)

    def _decode_ampersands(self, url):
        return re.sub(r'\\u0026', '&', url)

    def _get_image(self, url):
        url = self._decode_ampersands(url)
        request = requests.get(url, cookies=self._cookies)

        # Build image from binary response data
        image = Image.open(BytesIO(request.content))
        fp = tempfile.NamedTemporaryFile(prefix='basketcase_', suffix='.jpg', dir=self._output_images, delete=False)
        image.save(fp, format='JPEG')

    def _get_video(self, url):
        url = self._decode_ampersands(url)

        # Add the cookie header
        youtube_dl.utils.std_headers['Cookie'] = 'sessionid=' + self._cookies['sessionid']

        ydl_opts = {
            'outtmpl': self._output_videos + '/%(title)s.%(ext)s' # Set output directory
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

