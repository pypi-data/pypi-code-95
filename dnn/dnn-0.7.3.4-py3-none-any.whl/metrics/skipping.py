# Feb 3, 2021, Hans Roh
# confidence base skipping prediction stategy

import numpy as np
from sklearn.metrics import f1_score
from rs4.termcolor import tc
from dnn.callbacks import confusion_matrix
import copy
from importlib import reload

reload (confusion_matrix); print ('remove reload', __file__)

MIN_CONFIDENCE = 20
MAX_CONFIDENCE = 50
CONFIDENCE_INTERVAL = 6

def build_confidence_testset (n_classes):
    testset = set ()
    for k in range (MIN_CONFIDENCE, MAX_CONFIDENCE, CONFIDENCE_INTERVAL):
        for i in range (n_classes):
            origin = [k / 100. for _ in range (n_classes)]
            for j in range (MIN_CONFIDENCE, MAX_CONFIDENCE, CONFIDENCE_INTERVAL):
                current = origin [:]
                current [i] = j / 100.
                testset.add (tuple (current))
                for m in range (n_classes):
                    if k == m: continue
                    current = current [:]
                    current [m] = j / 100.
                    testset.add (tuple (current))
    return testset

def metric (labels, max_skip = 0.3, monitor_skip = 0.3, index = 0, skiptest = None):
    label = labels [index]
    confidence_testset = build_confidence_testset (len (label))

    def accuracy (y_true, y_pred, logs = None):
        if isinstance (y_true, tuple):
            y_true, y_pred = y_true [index], y_pred [index]
        logs = logs or {}
        labels = np.argmax (y_true, axis = 1)
        preds = np.argmax (y_pred, axis = 1)
        logs ['val_unskipped_acc'] = np.mean (labels == preds)
        logs ['val_unskipped_f1'] = f1_score (labels, preds, average = "weighted")

        cache = []
        for idx, y in enumerate (labels):
            logit = y_pred [idx]
            b = np.argsort (logit)[::-1]
            p, s = logit [b [0]], logit [b [1]]
            cache.append ((y, b [0], b [1], p, s, logit))

        sortkey = lambda x: (-x [0][1], -x [1][1], x [4][1], x [3][1])
        cands = {i: [] for i in range (int (max_skip * 10))}
        for diff in range (11, 15):
            diff_threshold = diff / 10.
            for min_confidence in confidence_testset:
                acc, y_true, y_pred, canceled, y_score = [], [], [], {}, []
                for y, pe, se, p, s, score in cache:
                    class_name = label.class_name (pe)
                    if class_name not in canceled:
                        canceled [class_name] = 0
                    if s * diff_threshold > p or p < min_confidence [pe]:
                        if y == pe:
                            canceled [class_name] += 1
                        continue
                    y_true.append (y)
                    y_pred.append (pe)
                    y_score.append (score)
                    acc.append (y == pe)

                dropped = len (labels) - len (y_true)
                share = (
                    ('confusing threshold', diff_threshold), ('confidences', min_confidence),
                    ('skip rate', dropped / len (labels)),
                    (y_true, y_pred, y_score)
                )
                rg = int (dropped / len (labels) * 10)
                if rg not in cands:
                    continue
                cands [rg].append ((('f1', f1_score (y_true, y_pred, average = "weighted")), ('accuracy', np.mean (acc))) + share)
                cands [rg] = [sorted (cands [rg], key = sortkey) [0]]

        info = []
        monitor_cands = []
        skip_cache = []
        if skiptest is not None:
            for logit in skiptest:
                b = np.argsort (logit)[::-1]
                p, s = logit [b [0]], logit [b [1]]
                skip_cache.append ((b [0], b [1], p, s))

        skipped_metrics = {}
        for rg in range (1, int (max_skip * 10)):
            if not cands [rg]:
                continue
            top = sorted (cands [rg], key = sortkey) [0]
            if top [4][1] < monitor_skip:
                monitor_cands.append (top)

            min_confidence = top [3][1]
            diff_threshold = top [2][1]
            y_true, y_pred, y_score = top [-1]

            base_metrics = {'skip rate': top [4][1], 'confidences': min_confidence, 'confusing threshold': diff_threshold}
            if skip_cache:
                skip_acc = [ s * diff_threshold > p or p < min_confidence [pe] for pe, se, p, s in skip_cache ]
                base_metrics ['skip acc'] = np.mean (skip_acc)
            buffer, metrics = confusion_matrix.plot_text (y_true, y_pred, label, base_metrics = base_metrics, return_metrics = True, y_score = np.array (y_score))
            info.append ('skipped confusion matrix:\n{}\n\n'.format (buffer))
            skipped_metrics [rg] = metrics

        info = " - ".join (info)
        print ('\n  - ' + info)
        try:
            top = sorted (monitor_cands, key = sortkey) [0]
        except IndexError:
            logs ['val_skip_rate'] = 0.0
            logs ['val_skiped_acc'] = 0.0
            logs ['val_skiped_f1'] = 0.0
        else:
            logs ['val_skip_rate'] = top [4][1]
            logs ['val_skiped_acc'] = top [1][1]
            logs ['val_skiped_f1'] = top [0][1]

        return skipped_metrics
    return accuracy
