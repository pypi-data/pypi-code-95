import cv2
from rs4 import attrdict

class VideoReader:
    def __init__ (self, fn):
        self.fn = fn
        self.vidcap = cv2.VideoCapture (fn)
        self.info = get_info (self.fn)

    def __del__ (self):
        self.vidcap.release ()

    def __len__ (self):
        return int (self.info ['video_length'] * self.info ['frame_rate'])

    def __getattr__ (self, attr):
        # {'frame_rate': 5.0, 'frame_width': 1080.0, 'frame_height': 1920.0, 'video_length': 2.8, 'format': 0.0, 'codec': 1983148141.0}
        try:
            return self.info [attr]
        except KeyError:
            raise AttributeError (attr)

    def __iter__ (self):
        while (self.vidcap.isOpened ()):
            ret, frame = self.vidcap.read ()
            frame_no = int (self.vidcap.get(1))
            if not ret:
                break
            yield frame


def capture (path, interval = 10):
    count = 0
    vidcap = cv2.VideoCapture (path)
    latest = 0
    frames = []
    while (vidcap.isOpened ()):
        ret, image = vidcap.read ()
        frame_no =  int (vidcap.get(1))
        if latest == frame_no:
            break
        latest = frame_no
        if frame_no % interval == 0:
            #print('Saved frame number : ' + str(int(vidcap.get(1))))
            frames.append (image)
            #cv2.imwrite("./images/frame%d.jpg" % count, image)
            #print('Saved frame%d.jpg' % count)
            count += 1
    vidcap.release ()
    return frames

def get_info (path):
    vidcap = cv2.VideoCapture (path)
    d = attrdict.AttrDict ()
    d.frame_rate = vidcap.get (cv2.CAP_PROP_FPS)
    d.frame_width = vidcap.get (cv2.CAP_PROP_FRAME_WIDTH)
    d.frame_height = vidcap.get (cv2.CAP_PROP_FRAME_HEIGHT)
    d.video_length = vidcap.get (cv2.CAP_PROP_FRAME_COUNT)  / d.frame_rate
    d.format = vidcap.get (cv2.CAP_PROP_FORMAT)
    d.codec = vidcap.get (cv2.CAP_PROP_FOURCC )
    return d
