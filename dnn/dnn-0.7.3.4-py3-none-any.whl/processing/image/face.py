import cv2
import tensorflow as tf
import os
from . import measure, img_util, facenet
from ..video import vtool
import threading
import random
import tempfile
import numpy as np
from scipy import spatial
import rs4
from sklearn.cluster import DBSCAN
import sys
from tfserver import cli
import multiprocessing as mp
LOCK = threading.Lock ()
ALIAS = 'face-detector'
DETECTOR = None
ENCODER = None
DEFAULT_FACE_SIMILARITY_THRESHOLD = 0.22
USE_TF_V1 = False


class Model:
    def __init__ (self, type = 'MTCNN'):
        if type == 'MTCNN':
            from fdet import MTCNN
            # from mtcnn_cv2 import MTCNN
            self._model = MTCNN ()
        elif type == 'RETINAFACE':
            from .retinaface import RetinaFace; import dnn; dnn.setup_gpus ()
            self._model = RetinaFace ()
        else:
            raise NameError ('Unknown model type')

    def __getattr__ (self, name):
        return getattr (self._model, name)

    def predict (self, inputs, *args, **kargs):
        results = self._model.detect (load (inputs ['x'].astype (np.uint8)))
        if not results:
            return dict (
                box = np.array ([]),
                confidence = np.array ([]),
                keypoints = np.array ([])
            )

        boxes, landms, confidences = [], [], []
        for result in results:
            confidences.append (result ['confidence'])
            boxes.append (result ['box'])

            landm = result ['keypoints']
            landms.append (np.concatenate ([
                landm ['left_eye'], landm ['right_eye'],
                landm ['nose'],
                landm ['mouth_left'], landm ['mouth_right']
            ]))

        return dict (
            box = np.array (boxes),
            confidence = np.array (confidences),
            keypoints = np.array (landms)
        )

    def close (self):
        self._model = None


def initialize_detector (model_type = 'MTCNN'):
    global DETECTOR, LOCK
    with LOCK:
        if DETECTOR is not None:
            return
        DETECTOR = Model (model_type)

def register_to_tfserver (model_type = 'MTCNN'):
    import tfserver

    initialize_detector (model_type)
    tfserver.register_model (ALIAS, DETECTOR)

def disable_v2_behavior ():
    global USE_TF_V1
    USE_TF_V1 = True

def load (pixels):
    if isinstance (pixels, str):
        pixels = cv2.imread (pixels)
    if pixels.shape [-1] != 3:
        temp = ".face-{}.bmp".format (next (tempfile._get_candidate_names()))
        try:
            cv2.imwrite (temp, pixels)
            pixels = cv2.imread (temp)
        finally:
            os.remove (temp)
    return cv2.cvtColor (pixels, cv2.COLOR_BGR2RGB)

def _detect_faces (image):
    initialize_detector ()
    if isinstance (image, list):
        if hasattr (DETECTOR, 'batch_detect'): #fdet
            return [ r [:1] for r in DETECTOR.batch_detect (image) ]
        else:
            return [ DETECTOR.detect_faces (each) [:1] for each in image ] # mtcnn
    method = DETECTOR.detect if hasattr (DETECTOR, 'detect') else  DETECTOR.detect_faces
    return method (image) [:1]

def detectall (pixels):
    # crop and strech
    image = load (pixels)
    result = _detect_faces (image)
    if result:
        result.sort (key = lambda x: x ['box'][3] * x ['box'][2], reverse = True)
    return result

def crop_face (image, result, resize):
    result.sort (key = lambda x: x ['box'][3] * x ['box'][2], reverse = True)
    bb = result [0]['box']
    x = max (0, bb [0])
    y = max (0, bb [1])
    crop_img = image [y:y + bb [3], x:x + bb [2]]
    if not resize:
        return crop_img
    img = img_util.resize (crop_img, resize)
    return img

def detect (pixels, resize = (48, 48)):
    # crop and strech
    image = load (pixels)
    result = _detect_faces (image)
    img = crop_face (pixels, result, resize) if result else None
    return result, img

def request_grpc (stub, x):
    try:
        resp = stub.predict (ALIAS, 'predict', x = x)
    except:
        return []
    if resp.status != 1.0:
        return []
    k = resp.keypoints.astype (np.int32).tolist ()
    top = dict (
        box = resp.box.astype (np.int32).tolist (),
        confidence = float (resp.confidence),
        keypoints = dict (
            left_eye = k [0:2],
            right_eye = k [2:4],
            nose = k [4:6],
            mouth_left = k [6:8],
            mouth_right = k [8:10],
        )
    )
    return [top]

def detect_batch (frames, resize = (48, 48), return_origin = False, stub = None):
    images = [ load (pixels) for pixels in frames ]
    if stub is None:
        results = _detect_faces (images)
    else:
        results = []
        for x in images:
            result = request_grpc (stub, x)
            results.append (result)

    batch = []
    for idx, result in enumerate (results):
        if not result:
            continue
        pixels = frames [idx]
        batch.append ((pixels if return_origin else None, result, crop_face (pixels, result, resize)))
    return batch

def detect_keep_ratio (pixels, resize = (48, 48)):
    image = load (pixels)
    result = _detect_faces (image)
    img = None
    if result:
        result.sort (key = lambda x: x ['box'][3] * x ['box'][2], reverse = True)
        iw, ih = image.shape [:2]
        bb = result [0]['box']
        x = max (0, bb [0])
        y = max (0, bb [1])
        x_ = min (iw, x + bb [2])
        y_ = min (ih, y + bb [3])
        width = x_ - x
        height = y_ - y

        # pad 15%
        y = max (0, y - int (height * 0.06))
        y_ = min (ih, y_ + int (height * 0.06))
        height = y_ - y

        if width > height:
            pad = (width - height) // 2
            y -= pad; y_ += pad
            y = max (0, y); y_ = min (ih, y_)
        else:
            pad = (height - width) // 2
            x -= pad; x_ += pad
            x = max (0, x); x_ = min (iw, x_)

        crop_img = image [y:y_, x:x_]
        if not resize:
            return result, crop_img
        img = cv2.resize (crop_img, resize)
    return result, img

def mark (pixels):
    image = load (pixels)
    result = _detect_faces (image)
    if not result:
        return
    else:
        bounding_box = result [0]['box']
        keypoints = result[0]['keypoints']
        cv2.rectangle (image,
                      (bounding_box[0], bounding_box[1]),
                      (bounding_box[0] + bounding_box[2], bounding_box[1] + bounding_box[3]),
                      (0,155,255),
                      2)
        cv2.circle (image, (keypoints['left_eye']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['right_eye']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['nose']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['mouth_left']), 2, (0,155,255), 2)
        cv2.circle (image, (keypoints['mouth_right']), 2, (0,155,255), 2)
    return image

DETECT_BATCH = 8

def _normalize (pixels, orientation, max_size = 480):
    if orientation:
        pixels = img_util.roate_ccw_by_90_degree (pixels, orientation)
    if np.max (pixels.shape) > max_size:
        resize_factor = [-1, -1]
        resize_factor [np.argmax (pixels.shape)] = max_size
        pixels = img_util.resize (pixels, tuple (resize_factor))
    return pixels

def from_imagelist_with_metric (images, orientation, resize = (48, 48), limit = 0, grpc_endpoint = None):
    grpc = cli.Server (grpc_endpoint) if grpc_endpoint else None
    faces = []
    frames = []
    for idx, pic in enumerate (images):
        pixels = _normalize (cv2.imread (pic), orientation)
        frames.append (pixels)
        if len (frames) == DETECT_BATCH:
            faces.extend (detect_batch (frames, resize = resize, stub = grpc))
            frames = []
        if limit and len (faces) >= limit:
            faces = faces [:limit]
            frames = []
            break

    if frames:
        faces.extend (detect_batch (frames, resize = resize, stub = grpc))
        frames = []

    faces = [(result, img) for _, result, img in faces]
    return faces

def from_video_with_metric (video, frame_skip = 10, min_width = 48, min_dist = DEFAULT_FACE_SIMILARITY_THRESHOLD, resize = (48, 48), with_marked = False, choice = 'maxdistance', orientation = 0, limit = 0, grpc_endpoint = None):
    grpc = cli.Server (grpc_endpoint) if grpc_endpoint else None
    hashes = []
    faces = []
    hashmap = {}
    markeds = []
    cluster = []
    frames = []
    detected = []
    for idx, pixels in enumerate (vtool.capture (video, frame_skip)):
        pixels = _normalize (pixels, orientation)
        frames.append (pixels)
        if len (frames) == DETECT_BATCH:
            detected.extend (detect_batch (frames, resize = resize, return_origin = with_marked, stub = grpc))
            frames = []
        if limit and len (detected) >= limit:
            detected = detected [:limit]
            frames = []
            break

    if frames:
        detected.extend (detect_batch (frames, resize = resize, return_origin = with_marked, stub = grpc))
        frames = []

    for pixels, result, img in detected:
        bb = result [0]['box']
        if bb [2] < min_width:
            continue
        h = measure.average_hash (img)
        hashmap [id (h)] = (img, pixels, result)

        if choice == "maxdistance":
            dup = False
            for h_ in hashes:
                dist = measure.hamming_dist (h, h_)
                if dist < min_dist:
                    #print ("threshold", dist)
                    dup = True
                    break

            hashes.append (h)
            if not dup:
                faces.append ((result, img))
                if with_marked:
                    markeds.append (mark (pixels))

        elif choice == "all":
            faces.append ((result, img))
            if with_marked:
                markeds.append (mark (pixels))

        elif choice.startswith ("single"):
            if len (cluster) == 0:
                cluster.append ([h])
                continue

            clustered = False
            for hashes in cluster:
                for h_ in hashes:
                    dist = measure.hamming_dist (h, h_)
                    if dist < min_dist:
                        hashes.append (h)
                        clustered = True
                        break

            if not clustered: # new cluster
                cluster.append ([h])

    def choose (dominent, count = 8):
        if len (dominent) <= 8:
            return dominent
        chosen = []
        th = count / len (dominent)
        for each in dominent:
            if random.random () <= th:
                chosen.append (each)
        return chosen [:count]

    persons = len (cluster)
    if choice.startswith ("single") and cluster:
        dominent = sorted (cluster, key = lambda x: len (x))[-1]
        for h in choose (dominent, 8):
            img, pixels, result = hashmap [id (h)]
            faces.append ((result, img))
            if with_marked:
                markeds.append (mark (pixels))
        #print ('face reducing: {} => {}'.format (len (dominent), len (faces)))

    r = faces
    if with_marked:
        r = (faces, markeds)
        if choice == 'single_with_count':
            r = (faces, markeds, persons)
    elif choice == 'single_with_count':
        r = (faces, persons)
    return r

def from_video (video, frame_skip = 10, min_width = 48, min_dist = DEFAULT_FACE_SIMILARITY_THRESHOLD, resize = (48, 48), with_marked = False, choice = 'maxdistance', orientation = 0):
    faces = from_video_with_metric (video, frame_skip, min_width, min_dist, resize, with_marked, choice, orientation)
    return [img for metric, img in faces]


ALIGN_IMAGE_SIZE = 160 # constant
ALIGN_MARGIN = 44 # constant

def embed (img, box = None):
    global ENCODER
    if ENCODER is None:
        ENCODER = facenet.Facenet ()

    if box is not None:
        det = box
    else:
        r = detectall (img)
        if not r:
            return
        det = r [0]['box']

    img_size = np.asarray (img.shape) [:2]
    x = np.maximum (det [0] - ALIGN_MARGIN//2, 0)
    y = np.maximum (det [1] - ALIGN_MARGIN//2, 0)
    x2 = np.minimum (x + det [2] + ALIGN_MARGIN//2, img_size [1])
    y2 = np.minimum (y + det [3] + ALIGN_MARGIN//2, img_size [0])
    cropped = img [y:y2,x:x2]
    aligned = cv2.resize (cropped, (ALIGN_IMAGE_SIZE, ALIGN_IMAGE_SIZE))
    embedding = ENCODER.embed_aligned (facenet.prewhiten (aligned))
    return embedding [0], aligned

def distance (a, b):
    return np.sqrt (np.sum (np.square (np.subtract (a, b))))

def cosine_distance (a, b):
    return spatial.distance.cosine(a, b)

hash = measure.average_hash
hamming_distance = measure.hamming_dist


def cluster (images, supplements = [], diff_threshold = 0.1, tails_to_compare = 0, dropout = 0.1):
    hashes = []
    er, tt = 0, 0
    for jpg in rs4.tqdm (images, desc = 'embedding'):
        tt += 1
        im = cv2.imread (jpg)
        _, fa = detect (im)
        if not _:
            er += 1
            continue

        eb, _ = embed (im, _ [0]['box'])
        if supplements:
            eb = eb.tolist ()
            eb.extend (supplements [tt - 1])
        h = measure.average_hash (fa)
        hashes.append ((jpg, eb, h))

    # optimal eps is 0.37, see https://gitlab.com/semiconnetworks/aimd/-/issues/40
    dbscan = DBSCAN (eps = 0.37, n_jobs = -1)
    dbscan.fit ([each [1] for each in hashes])
    y_pred = dbscan.labels_.astype (np.int)

    cluster = [[] for _ in range (np.max (y_pred) + 1)]
    for idx, y in enumerate (y_pred):
        if y == -1:
            continue
        cluster [y].append (hashes [idx])

    cluster = sorted (cluster, key = lambda x: len (x), reverse = 1)
    CLUSTER_THRESHOLD = int (sum ([len (each) for each in cluster [:3]]) // 3 * dropout)
    _cluster = []
    _dropped = 0
    for each in cluster:
        if len (each) > CLUSTER_THRESHOLD:
            _cluster.append (each)
        else:
            _dropped += 1
    cluster = _cluster
    print ("outlying clusters:", _dropped)
    print ('clustered:', len (cluster), 'error', er)

    _cluster = []
    for idx, _c in enumerate (cluster):
        origin = len (_c)
        uniques = [_c [0]]
        _h = _c [0][2]
        for current in _c [1:]:
            sim = False
            for unique in uniques [-tails_to_compare:]:
                dist = measure.hamming_dist (current [2], unique [2])
                if dist < diff_threshold:
                    sim = True
                    break
            not sim and uniques.append (current)
        print ('- cluster #{}: {} => {}'.format (idx, origin, len (uniques)))
        _cluster.append ([u [0] for u in uniques])
    return _cluster


if __name__ == '__main__':
    im = cv2.imread (os.path.join (os.path.dirname (__file__), 'facenet', "Anthony_Hopkins_0001.jpg"))
    emb = embed (im)
    print (emb)
    print (emb.shape)
    print (distance (emb, emb))


