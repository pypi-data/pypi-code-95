import os
import cv2
import numpy as np

SUSPENSION = 3
MAX_SKEW = 3
MIN_CAMS = 3
BOUNDARY_DIFF = 2

def isrect (points, imsize):
    xs = points [:,0,0]
    ys = points [:,0,1]

    w = max (xs) - min (xs)
    h = max (ys) - min (ys)
    flagpoint = (min (xs) - SUSPENSION, min (ys) - SUSPENSION)

    if w < 80 or h < 80: # too small
        return

    h_, w_ = imsize * 0.52 # too big
    if w > w_ or h > h_:
        return

    if not (0.35 < w / h < 2.5): # invalid screen ratio
        return

    # all point must be greater than falgpoint
    if len (xs [xs < flagpoint [0]]):
        return
    if len (xs [ys < flagpoint [1]]):
        return

    # at least one point is same as flagpoint
    if np.sum (np.abs (xs - min (xs)) <= MAX_SKEW) < 2:
        return
    if np.sum (np.abs (xs - max (xs)) <= MAX_SKEW) < 2:
        return
    if np.sum (np.abs (ys - min (ys)) <= MAX_SKEW) < 2:
        return
    if np.sum (np.abs (ys - max (ys)) <= MAX_SKEW) < 2:
        return

    # simplify rectacle
    rect = np.array ([
        [[min (xs), min (ys)]],
        [[min (xs), max (ys)]],
        [[max (xs), max (ys)]],
        [[max (xs), min (ys)]]
    ])
    return rect

def trim_around_black (im, T = False):
    if T:
        im = im.swapaxes (1, 0)

    imgray = cv2.cvtColor (im, cv2.COLOR_BGR2GRAY)
    h, w = imgray.shape
    start, end = 0, h

    if np.sum (im [0] > 30) == 0:
        for rownum in range (len (imgray) - 1):
            dual = imgray [rownum:rownum + 2].astype (np.int8)
            diff = np.sum (np.abs (dual [0] - dual [1]) > 2) / w
            if diff > 0.02:
                start = max (0, rownum - 10)
                break

    if np.sum (im [-1] > 30) == 0:
        for rownum in range (len (imgray) - 1, 0, -1):
            dual = imgray [rownum - 2:rownum].astype (np.int8)
            diff = np.sum (np.abs (dual [0] - dual [1]) > 2) / w
            if diff > 0.02:
                end = min (rownum + 10, h)
                break

    im = im [start:end]
    if T:
        im = im.swapaxes (1, 0)
    return im, (start, end)

def find_camera_visions (im, save_dir = None, image_index = 0):
    global BOUNDARY_DIFF

    im, (a, b) = trim_around_black (im)
    trimmed_top = a
    im, (a, b) = trim_around_black (im, True)
    trimmed_left = a

    imgray = cv2.cvtColor (im, cv2.COLOR_BGR2GRAY)
    save_dir and cv2.imwrite ('{}/img-{:03d}-imgray.jpg'.format (save_dir, image_index), imgray)
    h, w = imgray.shape

    # searching horizontal segments
    seps = [0]
    for rownum in range (len (imgray) - 1):
        if rownum == 0:
            continue
        dual = imgray [rownum:rownum + 2].astype (np.int16)
        if np.std (dual [1]) < 3:
            seps.append (rownum)
            continue
        diff = np.sum (np.abs (dual [0] - dual [1]) > BOUNDARY_DIFF) / w
        if diff > 0.7:
            seps.append (rownum)
    seps.append (h)

    seps_ = []
    voids = []
    for i in range (len (seps) - 1):
        rownum = seps [i]
        if seps [i + 1] - seps [i] == 1:
            voids.append (rownum)
        else:
            if voids:
                midval = voids [len (voids) // 2]
                seps_.append (midval)
                voids = []
            seps_.append (rownum)
    seps_.append (seps [-1])
    seps = seps_

    rows = []
    for i in range (len (seps) - 1):
        b, t = seps [i + 1], seps [i]
        if b - t >= 80:
            rows.append ((seps [i], b - t)) # (x-pos, row height)

    serial_rows = [
        [rows.pop (0)]
    ]
    while rows:
        cur_p, cur_h = serial_rows [-1][-1]
        nex_p, nex_h = rows [0]
        if nex_p - (cur_p + cur_h) > 48: # too wide gap between grid groups
            serial_rows.append ([rows.pop (0)])
            continue
        if not (0.75 < cur_h / nex_h < 1.3): # row height is too different
            serial_rows.append ([rows.pop (0)])
            continue
        serial_rows [-1].append (rows.pop (0))

    rows = []
    for rowg in serial_rows:
        if len (rowg) == 1: # at least 2 rows
            continue
        if rowg [0][0] > h * 0.5: # too lower position
            continue
        if sum (rowg [-1]) < h * 0.5:  # too high position
            continue
        rows.extend (rowg)

    if len (rows) <= 1:
        return []

    # retrimming for precise target grid group
    top_trim_pixel = max (0, rows [0][0] - 20)
    bot_trim_pixel = min (sum (rows [-1]) + 20, h)
    rows = [(_p - top_trim_pixel, _h) for _p, _h in rows ]
    im = im [top_trim_pixel: bot_trim_pixel]

    # refresh gray image
    imgray = cv2.cvtColor (im, cv2.COLOR_BGR2GRAY)
    save_dir and cv2.imwrite ('{}/img-{:03d}-imgray.jpg'.format (save_dir, image_index), imgray)
    h, w = imgray.shape

    # create mask for contouring
    mask = np.zeros (imgray.shape, dtype = np.uint8)
    mask [:] = [255]

    # searching vertical segments
    macros = [0]
    T = imgray.swapaxes (1, 0)
    for colnum in range (len (T) - 1):
        dual = T [colnum:colnum + 2].astype (np.int16)
        if np.std (dual [1]) < 3:
            macros.append (colnum)
            continue
        diff = np.sum (np.abs (dual [0] - dual [1]) > BOUNDARY_DIFF) / h
        if len (rows) == 2:
            threshold = 0.45
        else:
            threshold = min (0.7, (1 - 1 / (len (rows) + 1)))
        if diff > threshold:
            macros.append (colnum)
    macros.append (w)

    # masking
    cv2.line (mask, (4, 0), (4, h), 0, 8)
    cv2.line (mask, (w - 4, 0), (w - 4, h), 0, 8)
    for idx, (t, he) in enumerate (rows):
        b = t + he
        cv2.line (mask, (0, t), (w, t), 0, 8)
        cv2.line (mask, (0, b), (w, b), 0, 8)

        row = imgray [t:b].swapaxes (1, 0)
        for colnum in range (len (row) - 1):
            dual = row [colnum:colnum + 2].astype (np.int16)
            diff = np.sum (np.abs (dual [0] - dual [1]) > BOUNDARY_DIFF) / row.shape [1]
            if diff > 0.75 and colnum in macros:
                cv2.line (mask, (colnum, t), (colnum, b), 0, 8)

    # detect video areas
    contours, hierachy = cv2.findContours (mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    save_dir and cv2.imwrite ('{}/img-{:03d}-mask.jpg'.format (save_dir, image_index), mask)
    smoothing = []
    imsize = np.array (imgray.shape, dtype = np.float32)
    for each in contours:
        rect = isrect (each, imsize)
        if rect is not None:
            smoothing.append (rect)
    contours = np.array (smoothing)
    contoured = cv2.drawContours (im.copy (), contours, -1, (255, 0, 0), 3)
    save_dir and cv2.imwrite ('{}/img-{:03d}-contoured.jpg'.format (save_dir, image_index), contoured)

    coords = []
    for box in contours:
        coords.append ([(p [0][0] + trimmed_left, p [0][1] + trimmed_top + top_trim_pixel) for p in box])
    coords.sort (key = lambda x: (round (x [0][1] / 10), round (x [0][0] / 10)))
    return np.array (coords)

