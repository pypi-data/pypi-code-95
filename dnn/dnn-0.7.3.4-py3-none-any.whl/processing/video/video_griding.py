from rs4 import pathtool
import os
import shutil
import cv2
import numpy as np
import time
from . import ffmpeg, vtool
from ..image import face, camera_griding, img_util

class Griding:
    detect_interval = 30
    def __init__ (self, video, output, trimming = None, export_video = False, video_secs = 3.0, frame_limit = 0):
        assert video_secs < 7.0, 'video_secs should be less than 7.0'
        self.video = video
        self.output = output
        self.frame_limit = frame_limit
        self.trimming = trimming
        self.export_video = export_video
        self.clips = 0
        self.frame_rate = vtool.get_info (self.video).frame_rate
        self.video_length = ffmpeg.get_movie_length (self.video)
        self.video_frames = int (video_secs * self.frame_rate)
        self.min_frames = int (3.0 * self.frame_rate)
        self.audio = ".".join (self.video.split (".") [:-1]) + '.wav'
        self.total_time = 0
        self.positions = {}
        self.persons = {}
        self.video_total_time_stamp = time.strftime('%H:%M:%S', time.gmtime (self.video_length))

    def make_video (self, fn, frames):
        # clip id-camera position-frameno.mp4
        poster = '{}/{}/{}'.format (self.output, fn, frames [0])
        camera_no = fn [-2:]
        frame_no = int (frames [0][6:-4])
        temp = '{}/_{}.mp4'.format (self.output, fn)
        mp4 = '{}/{}-{:07d}.mp4'.format (self.output, fn, frame_no)

        use_frames = len (frames) if len (frames) < self.video_frames + self.min_frames else self.video_frames
        frames_to_consume, frames = frames [:use_frames], frames [use_frames:]
        if not self.export_video:
            return frames

        play_time = len (frames_to_consume) / self.frame_rate
        self.total_time += play_time
        print ('- creating video {}: {:.1f} secs (total {:.2f} mins)'.format (os.path.basename (mp4), play_time, self.total_time / 60))

        im = img_util.resize (cv2.imread (poster), (400, 0))
        h, w = im.shape [:2]

        out = cv2.VideoWriter (temp, cv2.VideoWriter_fourcc(*"mp4v"), self.frame_rate, (w, h))
        for idx, frame in enumerate (frames_to_consume):
            im = cv2.imread ('{}/{}/{}'.format (self.output, fn, frame))
            im = img_util.resize (im, (w, h))

            im = cv2.rectangle (im, (4, 0),  (21, 18), (117, 27, 20), -1)
            im = cv2.putText(im, camera_no, (7, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1, cv2.LINE_AA)
            time_stamp = time.strftime('%H:%M:%S', time.gmtime ((frame_no + idx) / self.frame_rate))
            ts = '{} of {}'.format (time_stamp, self.video_total_time_stamp)
            im = cv2.putText(im, ts, (27, 11), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (32, 32, 32), 1, cv2.LINE_AA)
            im = cv2.putText(im, ts, (26, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (168, 168, 168), 1, cv2.LINE_AA)
            im = cv2.rectangle (im, (0, h - 16),  (w, h - 2), (32, 32, 32), -1)

            copyblock_x = max (40, int (w * 0.16))
            copyblock_y = max (50, int (h * 0.2))
            im = cv2.putText(im, 'For A.I. Research And Development Purposes Only'.format (time_stamp, self.video_total_time_stamp), (max (copyblock_x + 8, (copyblock_x + 60) - (idx // 2)), h - 6), cv2.FONT_HERSHEY_PLAIN , 0.56, (128, 204, 97), 1, cv2.LINE_AA)
            im = cv2.rectangle (im, (4, h - copyblock_y), (copyblock_x, h), (174, 122, 0), -1)
            im = cv2.putText(im, 'SNS'.format (time_stamp, self.video_total_time_stamp), (8, (h - copyblock_y) + 14), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (227, 222, 208), 2, cv2.LINE_AA)

            out.write (im)
            # save poster image
            idx == 0 and cv2.imwrite ('{}/{}-{:07d}.jpg'.format (self.output, fn, frame_no), im)
        out.release ()
        ffmpeg.crop_wav (self.audio, temp + '.wav', frame_no / self.frame_rate, play_time)
        ffmpeg.mix_wav (temp, temp + '.wav', mp4)
        os.remove (temp)
        os.remove (temp + '.wav')

        return frames

    def validate (self):
        for fn in sorted (os.listdir (self.output)):
            clip = '{}/{}'.format (self.output, fn)
            if fn [0] in "_.":
                continue
            if not os.path.isdir (clip):
                continue
            if int (fn.split ('-')[0]) < self.clips:
                continue

            frames = sorted (os.listdir (clip))
            if len (frames) < self.min_frames:
                shutil.rmtree (clip)
                print ('- clip {} removed: {:,} frames'.format (fn, len (frames)))
                continue

            detected = []
            for idx in range (0, len (frames), 5):
                im = cv2.imread ('{}/{}/{}'.format (self.output, fn, frames [idx]))
                imgray = cv2.cvtColor (im, cv2.COLOR_BGR2GRAY)
                detected.append ((imgray > 127).sum () / np.product (imgray.shape) > 0.1)

            if np.sum (detected) == 0:
                shutil.rmtree (clip)
                print ('- clip {} removed: black screen'.format (fn))
                continue

            generatables = 0
            while frames:
                detected = -1
                for idx in range (0, len (frames), 5):
                    frame = '{}/{}'.format (clip, frames [idx])
                    im = cv2.imread (frame)
                    r = face.detectall (im)
                    if r:
                        detected = idx
                        break

                if detected == -1 or len (frames [detected:]) < self.min_frames:
                    detected = len (frames)
                deletables, frames = frames [:detected], frames [detected:]
                for frame in deletables:
                    os.remove ('{}/{}'.format (clip, frame))
                if not frames:
                    break

                generatables += 1
                frames = self.make_video (fn, frames)

            if self.export_video or not generatables:
                if not generatables:
                    print ('- clip {} removed: no faces or too lack'.format (fn))
                shutil.rmtree (clip)

    def _extract (self):
        latest = []
        boxes = []
        accumulated = 0
        vidcap = cv2.VideoCapture (self.video)
        while (vidcap.isOpened ()):
            ret, im = vidcap.read ()
            if not ret: break

            completed_frame = int (vidcap.get(1))
            if len (boxes) == 0 or completed_frame % self.detect_interval == 0:
                _boxes = camera_griding.find_camera_visions (img_util.trim (im, self.trimming), not self.export_video and self.output or None, self.clips)
                current = np.array ([b [0] for b in _boxes])

                if len (latest) != len (current) or np.mean (np.abs (latest - current)) > 8 or accumulated > (30 * 60 * 1):
                    self.validate ()
                    self.clips += len (latest)
                    latest = current
                    boxes = _boxes # refresh boxes
                    new_clip_ids = []
                    accumulated = 0
                    for idx, box in enumerate (boxes):
                        clip_id = self.clips + idx
                        new_clip_ids.append (clip_id)
                        pathtool.mkdir ('{}/{:04d}-{:02d}'.format (self.output, clip_id, idx + 1))
                    print ('new clips created:', new_clip_ids)

            accumulated += 1
            for idx, box in enumerate (boxes):
                clip_id = self.clips + idx
                x1, y1 = box [0]
                x2 = box [-1][0]
                y2 = box [1][1]
                vision = im [y1:y2,x1:x2]
                cv2.imwrite ('{}/{:04d}-{:02d}/frame-{:07d}.jpg'.format (self.output, clip_id, idx + 1, completed_frame), vision)

            if self.frame_limit and completed_frame > self.frame_limit:
                break

        self.validate ()
        vidcap.release ()

    def extract (self):
        ffmpeg.extract_wav (self.video, self.audio)
        try:
            self._extract ()
        finally:
            os.remove (self.audio)
