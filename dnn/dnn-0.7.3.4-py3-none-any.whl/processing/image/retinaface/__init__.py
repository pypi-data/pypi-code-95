from tfserver import service_models
import os

class RetinaFace:
    def __init__ (self, face_threshhold = 0.5):
        self.face_threshhold = face_threshhold
        self.model = service_models.load (os.path.join (os.path.dirname (__file__), 'model'))

    def detect (self, img):
        h, w = img.shape [:2]
        valids = []
        for r in self.model.predict (img):
            if r ['confidence'] < self.face_threshhold:
                continue
            # adjust mtcnn and retinaface bbox gaps
            bbox = r ['box']
            h_offset, w_offset = int (bbox [3] * 0.025), int (bbox [2] * 0.05)
            r ['box'] = (
                max (0, bbox[0] - w_offset),
                min (w, bbox[2] + h_offset),
                max (0, bbox[1] + w_offset),
                min (h, bbox[3] - h_offset),
            )
            valids.append (r)
        return valids

    def batch_detect (self, imgs):
        return [ self.model.predict (img) for img in imgs ]


if __name__ == '__main__':
    f = RetinaFace ()
