from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import numpy as np
import pandas as pd

from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, roc_auc_score, recall_score, precision_score, f1_score
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.calibration import calibration_curve

from pprint import pprint
from .utils import in_ipynb, eprint, keydefaultdict, display

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from collections import defaultdict, ChainMap, Counter

from typing import List, Dict, Any, Union

BINARY_BIN_NAMES = ['No', 'Yes']

DISCRETE_GENERIC_BIN_NAMES = keydefaultdict(
    lambda n: ['Level {}'.format(i) for i in range(n)], {
        2: ['low', 'high'],
        3: ['low', 'medium', 'high'],
        4: ['low', 'medium-low', 'medium-high', 'high'],
        5: ['very low', 'low', 'medium', 'high', 'very high'],
        6: ['very low', 'low', 'medium-low', 'medium-high', 'high', 'very high'],
        7: ['very low', 'low', 'medium-low', 'medium', 'medium-high', 'high', 'very high'],
        8: ['very low', 'low', 'quite low', 'medium-low', 'medium-high', 'quite high', 'high', 'very high'],
        9: ['very low', 'low', 'quite low', 'medium-low', 'medium', 'medium-high', 'quite high', 'high', 'very high'],
    }
)


def get_discrete_labels(nb_bins, label_type='generic'):
    """"
        label_type:
            'generic': low, high, etc.
            'binary': No, Yes
            
    """
    if label_type == 'generic':
        return list(DISCRETE_GENERIC_BIN_NAMES[nb_bins])
    elif label_type == 'binary' and nb_bins == 2:
        return list(BINARY_BIN_NAMES)
    else:
        raise ValueError('Invalid label_type.')


def bucketize_into_bins(
    array,
    nb_bins,
    encode='ordinal',
    strategy='quantile',
    retbins=False,
    retlabels=False,
    label_type='interval',
    label_unit='',
    round_label=1,
):
    """
        strategy: 'uniform' (same length), 'quantile' (same nb items)
        encode: 'ordinal' or 'onehot'
        ret_bins: return also bins value
        retlabels : return also the bins labels
        label_type: 'interval' (the actual interval, e.g., 10-21), 'generic' (generic labels, e.g., low or high)

        Return 

        -------

        bucketize_array, (bins_values, )(labels, )
    """
    kbd = KBinsDiscretizer(n_bins=nb_bins, encode='ordinal', strategy=strategy)
    bucketized = kbd.fit_transform(np.array([np.array(array)]).T).flatten().astype(int)
    ret = [bucketized]

    # Bins values
    if retbins:
        bin_values = {i: (kbd.bin_edges_[0][i], kbd.bin_edges_[0][i + 1]) for i in range(kbd.n_bins_[0])}
        ret.append(bin_values)

    # Bins labels
    if retlabels:
        if label_type == 'interval':
            bin_labels = []
            for i in range(kbd.n_bins_[0]):
                a, b = round(kbd.bin_edges_[0][i], round_label), round(kbd.bin_edges_[0][i + 1], round_label)
                if round_label <= 0:
                    a, b = int(a), int(b)
                bin_labels.append(f"{a}-{b}{' ' if label_unit else ''}{label_unit}")
            ret.append(bin_labels)
        else:
            ret.append(get_discrete_labels(kbd.n_bins_[0], label_type))
    return ret if len(ret) > 1 else ret[0]


class MultiColumnLabelEncoderDecoder:
    """
        Encoder and Decoder for discrete DataFrames
        
    """
    def __init__(self, decoder: Union[Dict[Any, Dict[Any, Any]], None] = None):
        """
            decoder : dict of dicts (optional)
            of this kind:
            {
                feature_name : {
                    0: feature_value_name,
                    1: ...
                },
                ...
            }
        """

        self.decoder = decoder
        if self.decoder is not None:
            self.encoder = self.__enctodec_dectoenc(self.decoder)
        else:
            self.encoder = None

    def fit(self, X, columns_names=None):
        """"
            Fit a DataFrame a DataFrame of str (categorical)
            to the encoder/decoder

            It uses LabelEncoder under the hood.
            

        """
        assert isinstance(X, pd.DataFrame) or (
            columns_names is not None and not isinstance(X, pd.DataFrame)
        ), "You must pass a DataFrame or provide columns names"
        if self.encoder is not None:
            eprint('WARNING: Encoder alredy fitted. Re-fitting overwriting...')
        encoders = {}
        columns_names = X.columns.values if isinstance(X, pd.DataFrame) else columns_names
        for col in columns_names:
            le = LabelEncoder()
            le.fit(list(sorted(list(X[col]))))
            encoders[col] = le
        self.encoder = self.__generate_encoderdict_from_encoders(encoders)
        self.decoder = self.__enctodec_dectoenc(self.encoder)
        return True

    def encode(self, X, inplace=False):
        return self.__encode_decode(self.get_encoder(), X, inplace)

    def __onehot_columns_names(self, columns):
        return [col + '_' + self.decoder[col][i] for col in columns for i in range(len(self.encoder[col]))]

    def encode_onehot(self, X, inplace=False):
        # Number of encodings per features
        nb_encs = [len(self.encoder[col]) for col in X.columns.values]
        # Encodings offset
        offset = [0]
        for nb in nb_encs[:-1]:
            offset.append(offset[-1] + nb)
        # Column names
        columns_names = self.__onehot_columns_names(X.columns.values)

        # Encode
        X_oh = np.zeros((len(X), sum(nb_encs)))
        for i, x in enumerate(X.values):
            for j, xval in enumerate(x):
                X_oh[i, offset[j] + xval] = 1

        # Return a DataFrame
        return pd.DataFrame(X_oh, columns=columns_names, index=X.index)

    def decode(self, X, inplace=False):
        return self.__encode_decode(self.get_decoder(), X, inplace)

    def single_encode(self, col, val):
        return self.get_encoder()[col][val]

    def single_decode(self, col, val):
        return self.get_decoder()[col][val]

    def get_values(self, col):
        return np.array(list(self.encoder[col].keys()))

    def get_encodings(self, col):
        return np.arange(len(self.get_values(col)))

    def get_nb_values(self, col):
        return len(list(self.encoder[col].keys()))

    def get_names(self):
        return {name: list(value_dict.values()) for name, value_dict in self.get_decoder().items()}

    @staticmethod
    def __encode_decode(d, X, inplace):
        if not inplace:
            X = X.copy()
        for col in X.columns.values:
            if col not in list(d.keys()):
                raise Exception('Column not found in the encoder/decoder keys!')
            X[col] = np.array([d[col][val] for val in X[col].values])
        return X

    def fit_encode(self, X):
        if self.fit(X):
            return self.encode(X)

    def get_decoder(self):
        if self.decoder is not None:
            return self.decoder
        else:
            raise Exception('ERROR: No decoder detected!')

    def get_encoder(self):
        if self.encoder is not None:
            return self.encoder
        else:
            raise Exception('ERROR: No encoder detected!')

    @staticmethod
    def __generate_encoderdict_from_encoders(encoders):
        encoder = {}
        for col, le in encoders.items():
            encoder[col] = {val: i for i, val in enumerate(list(le.classes_))}
        return encoder

    @staticmethod
    def __enctodec_dectoenc(d):
        r = {}
        for col in d.keys():
            r[col] = {y: x for x, y in d[col].items()}
        return r


# %%


def plot_feature_woe_bins(df, fname, target, nbins=20, nan_values=[], cut='qcut'):
    import plotly.express as px

    col = df[fname].copy()

    nan_values = ['NaN'] + nan_values
    nan_masks = [col.isnull()]
    # We replace all the values in nan_values with NaN and save the masks
    for val in nan_values[1:]:
        # Intervals (l, r), non-inclusive
        if isinstance(val, tuple):
            l, r = val
            if l is None and r is None:
                raise ValueError('Left and right value of an interval cannot be both none.')
            elif l is None:
                nan_mask = (col < r)
            elif r is None:
                nan_mask = (col > l)
            else:
                nan_mask = ((col < r) & (col > l))
        # Single values
        else:
            nan_mask = (col == val)
        # Append mask
        nan_masks.append(nan_mask)
        # Replace with NaN in the DF
        col = col.where(~nan_mask, other=np.nan)

    for i in range(len(nan_values) - 1, -1, -1):
        if nan_masks[i].sum() == 0:
            del nan_masks[i]
            del nan_values[i]

    # We bin the feature with q bins
    if cut == 'qcut':
        col, bn = pd.qcut(col, q=nbins, retbins=True, labels=np.arange(nbins))
    elif cut == 'cut':
        col, bn = pd.cut(col, bins=nbins, retbins=True, labels=np.arange(nbins))
    else:
        raise ValueError('Invalid cut type.')

    # NaN will have [-1, ..., -nb_nans]
    # If there is actual NaN, it will have index -1
    # Other nan_values will have bins [-2, ..., -1-len(nan_values)]
    for i, (value, mask) in enumerate(zip(nan_values, nan_masks)):
        col = col.where(~mask, other=-1 - i)

    # Cast to ingeger (should be alrady all intergers anyway)
    col = col.astype(int)

    # We get also the target columns
    tgt = df[target].values.copy()

    # Let's put the feature and the target together and count the occurences
    wdf = pd.DataFrame(np.array([tgt, col]).T, columns=['Target', 'Feature']).sort_values(['Target', 'Feature'])
    wdf['count'] = 1
    counts = wdf.groupby(['Feature', 'Target']).count()
    # Add zero counts for indexes (bins) that do not have any
    for i in set(list(range(nbins))) - set(np.array([i for i in counts.index.values])[:, 0]):
        counts.loc[(i, 0)] = 0

    woedf = counts.reset_index().pivot(index='Feature', columns='Target', values='count')
    woedf = woedf.rename(columns={0: 'Good', 1: 'Bad'})
    # NaN counts to 0
    woedf = woedf.fillna(0)

    woedf['Count'] = woedf['Good'] + woedf['Bad']
    woedf['Percentage'] = (woedf['Count'] / woedf['Count'].sum() *
                           100).apply(lambda x: (str(round(x, 2)) if round(x, 2) > 0 else '< 0.01') + '%')

    # Let's compute the WOE (disable error to get so log(0) = -inf)
    preverr_divide = np.geterr()['divide']
    np.seterr(divide='ignore')
    woedf['G/B Ratio'] = woedf['Good'] / woedf['Bad']
    woedf['WOE'] = np.log(woedf['G/B Ratio'])
    np.seterr(divide=preverr_divide)

    woemin = woedf['WOE'][np.isfinite(woedf['WOE'].values)].min()
    woemax = woedf['WOE'][np.isfinite(woedf['WOE'].values)].max()
    woedf['WOE'] = np.nan_to_num(
        woedf['WOE'].values,
        neginf=woemin - .25 * (woemax - woemin),
        posinf=woemax + .25 * (woemax - woemin),
    )

    # Replace zero counts with WOE = nan
    woedf['WOE'] = woedf['WOE'].where((woedf['Good'] != 0) | (woedf['Bad'] != 0), other=np.nan)

    # Let's create a marker column to color NaN differently
    woedf['Spec'] = list(map(lambda x: {True: 'Yes', False: 'No'}[x], (woedf.index.values < 0)))

    # Let's trandoform the bins [-1] (for NaN) and [0, ..., q-1] for the actual values
    # to strings with their intervals
    bins_names = np.array(
        [
            f"({val[0] if val[0] is not None else '-∞'}, {val[1] if val[1] is not None else '∞'})"
            if isinstance(val, tuple) else str(val) for val in nan_values
        ] + [f"({bn[i-1]}, {bn[i]}]" for i in range(1, len(bn))]
    )
    woedf[fname] = bins_names

    # Plot feature with WOE
    fig = px.bar(
        woedf[::-1],
        x='WOE',
        y=fname,
        orientation='h',
        height=200 + nbins * 18,
        color='Spec',
        title=f'WOE in {nbins} bins for \'{fname}\'',
    )

    # If there are NaN let's draw a vertical line
    for r, row in woedf[woedf.index.values < 0].iterrows():
        fig.add_shape(
            type="line",
            x0=row['WOE'],
            y0=0,
            x1=row['WOE'],
            y1=1,  # -1 is the NaN
            line=dict(
                color="Red",
                width=1,
                dash="dash",
            )
        )
        fig.update_shapes(dict(xref='x', yref='paper'))
    fig.show()

    return woedf.set_index(fname, drop=True)


def show_results_dataframe(results):
    if in_ipynb():
        summary = pd.DataFrame([results['total']])

        def get_filtered(filter, index=True):
            if index:
                filtered = summary[[col for col in summary if filter in col]]
                filtered.columns = [x.replace(filter + '_', '') for x in filtered.columns.values]
                filtered.index = [filter]
            else:
                filtered = summary[[col for col in summary if 'micro' not in col and 'macro' not in col]]
                filtered.index = ['']
            return filtered

        display(get_filtered('accuracy', index=False))
        display(pd.concat([get_filtered('macro'), get_filtered('micro')]))
        details = pd.DataFrame(results['per_class']).T
        details.columns = [x.replace('class_', '') if x != 'class_name' else x for x in details.columns.values]
        details.index.rename('class_id', inplace=True)
        display(details)

        print(
            'Precision PPV = TP / (TP + FP) = "How many of the selected items are relevant?" (Positive Predicted Value)'
        )
        print(
            'Recall    TPR = TP / (TP + FN) = "How many of the relevant items are selected?" (True Positive Rate, HIGH)'
        )
        print(
            'Fall-out  FPR = FP / (FP + TN) = "How many of the non-relevant items are selected?" (=1-Recall others, False Positive Rate, LOW)\n'
        )

    else:
        pprint(results)


# %%


def ml_report(y_true, y_predict, class_names, show=True, title=''):
    """
        ML algorithm personalized report
           - pandas DataFrame if in Notebook
           - Text if not
           
        Suitable for multi-class
    """

    # Pre-process and check inputs
    y_true, y_predict = np.array(y_true).flatten(), np.array(y_predict).flatten()
    assert len(y_true) == len(y_predict) > 0

    # Calculate class-wise stats
    results = {'per_class': dict(), 'total': dict()}
    for idx, cname in enumerate(class_names):
        true_pred = (y_true == y_predict)
        true_idx = (y_true == idx)
        pred_idx = (y_predict == idx)

        TP = np.sum(np.logical_and(true_pred, true_idx))
        class_precision = TP / np.sum(pred_idx) if np.sum(pred_idx) > 0 else 0.0
        class_recall = TP / np.sum(true_idx) if np.sum(true_idx) > 0 else 0.0
        class_f1 = 2 * class_precision * class_recall / (class_precision +
                                                         class_recall) if (class_precision + class_recall) > 0 else 0.0
        results['per_class'][idx] = {
            'class_name': cname,
            'true_positive': TP,
            'all_positive': np.sum(y_predict == idx),
            'all_true': np.sum(y_true == idx),
            'class_precision': class_precision,
            'class_recall': class_recall,
            'class_f1': class_f1
        }

    # Calculate global stats
    results['total']['macro_precision'] = np.mean(
        [results['per_class'][idx]['class_precision'] for idx in results['per_class']]
    )
    results['total']['macro_recall'] = np.mean(
        [results['per_class'][idx]['class_recall'] for idx in results['per_class']]
    )
    results['total']['macro_f1'] = 2 * results['total']['macro_precision'] * results['total']['macro_recall'] / (
        results['total']['macro_precision'] + results['total']['macro_recall']
    ) if (results['total']['macro_precision'] + results['total']['macro_recall']) > 0 else 0.0

    results['total']['accuracy'] = sum([results['per_class'][idx]['true_positive']
                                        for idx in results['per_class']]) / len(y_true)
    results['total']['n_samples'] = len(y_true)

    all_positive = np.sum([results['per_class'][idx]['all_positive'] for idx in results['per_class']])
    results['total']['micro_precision'] = np.sum(
        [results['per_class'][idx]['true_positive'] for idx in results['per_class']]
    ) / all_positive if all_positive > 0 else 0.0
    all_true = np.sum([results['per_class'][idx]['all_true'] for idx in results['per_class']])
    results['total']['micro_recall'] = np.sum(
        [results['per_class'][idx]['true_positive'] for idx in results['per_class']]
    ) / all_true if all_true > 0 else 0.0
    results['total']['micro_f1'] = 2 * results['total']['micro_precision'] * results['total']['micro_recall'] / (
        results['total']['micro_precision'] + results['total']['micro_recall']
    ) if (results['total']['micro_precision'] + results['total']['micro_recall']) > 0 else 0.0

    # Show confusion matrix
    if show and in_ipynb():
        from IPython.core.display import display, HTML
        display(HTML(f'<h2>Model Evaluation Report{title}</h2>'))

        import seaborn as sns

        plt.figure(figsize=(1.5 * len(class_names) + 1, 1.5 * len(class_names)))
        cm = confusion_matrix(y_true, y_predict)
        sns.heatmap(cm, annot=True, ax=plt.gca(), fmt='d')
        #annot=True to annotate cells
        plt.gca().set_xlabel('Predicted labels')
        plt.gca().set_ylabel('True labels')
        plt.gca().set_title('Confusion Matrix')
        plt.gca().xaxis.set_ticklabels(list(class_names))
        plt.gca().yaxis.set_ticklabels(list(class_names))
        plt.show()

    return results


def ml_report_probability(y_true, y_pred_proba, class_names, show=True, show_scatter=True, threshold=.5):
    # Preprocess Inputs
    y_true = np.array(y_true).flatten()
    y_pred_proba = np.array(y_pred_proba)
    assert len(y_pred_proba.shape) == 2
    assert len(class_names) == y_pred_proba.shape[1]
    assert len(y_true) == len(y_pred_proba)

    def get_colors_per_class(class_id):
        color_set = plt.get_cmap('Set1').colors
        color_a = np.array(list(color_set[class_id % len(color_set)]) + [1.00]).reshape(1, -1)
        color_b = np.array(list(color_set[class_id % len(color_set)]) + [0.10]).reshape(1, -1)
        color_c = np.array(list(color_set[class_id % len(color_set)]) + [0.60]).reshape(1, -1)

        return color_a, color_b, color_c

    n_samples, n_classes = y_pred_proba.shape

    if show and in_ipynb() and show_scatter:

        width = min(max(5, 1 * len(y_true) / 25), 25)
        plt.figure(figsize=(width, 5))
        for i, (true_class, pred_prob) in enumerate(zip(y_true, y_pred_proba)):
            probscatter = pred_prob[1] if n_classes == 2 else pred_prob[true_class]
            plt.scatter(
                i,
                probscatter,
                edgecolors=get_colors_per_class(true_class)[0],
                facecolors=get_colors_per_class(true_class)[1],
            )

        legend_elements = [
            Line2D(
                [0],
                [0],
                marker='o',
                color='w',
                label=class_name,
                markersize=8,
                markeredgecolor=get_colors_per_class(class_id)[0][0],
                markerfacecolor=get_colors_per_class(class_id)[1][0],
            ) for class_id, class_name in enumerate(class_names)
        ]
        #         plt.scatter(i, pred_prob[true_class], c=np.array(plt.get_cmap('Set1').colors[true_class]).reshape(1,-1), alpha = .1, edgecolors='none')
        if n_classes == 2:
            plt.axhline(y=threshold, color='black', linestyle='--', alpha=.35)
        plt.title('True class vs. probability')
        plt.ylabel('Probability (correct class)')
        plt.xlabel('Record IDs')
        plt.ylim(-.05, 1.05)
        plt.grid(alpha=.2)
        plt.gca().legend(handles=legend_elements, loc='best')
        plt.show()

    # Compute ROC curve and ROC area for each class
    fpr = dict()
    tpr = dict()
    thr = dict()
    roc_auc = dict()
    for i in range(n_classes):
        fpr[i], tpr[i], thr[i] = roc_curve(y_true == i, y_pred_proba[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    y_pred_proba_flat = y_pred_proba.flatten()
    y_true_flat = np.concatenate([y_true == i for i in range(n_classes)]).flatten()
    fpr["micro"], tpr["micro"], _ = roc_curve(y_true_flat, y_pred_proba_flat)
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

    # First aggregate all false positive rates
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

    # Then interpolate all ROC curves at this points
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(n_classes):
        mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])

    # Finally average it and compute AUC
    mean_tpr /= n_classes

    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(
        fpr["macro"],
        tpr["macro"],
    )

    # Plot all ROC curves
    if show and in_ipynb():
        plt.figure(figsize=(9, 5.5))
        plt.plot(
            fpr["micro"],
            tpr["micro"],
            label='micro-average ROC curve (area = {0:0.2f})'
            ''.format(roc_auc["micro"]),
            color='deeppink',
            linestyle=':',
            linewidth=2
        )

        plt.plot(
            fpr["macro"],
            tpr["macro"],
            label='macro-average ROC curve (area = {0:0.2f})'
            ''.format(roc_auc["macro"]),
            color='navy',
            linestyle=':',
            linewidth=2
        )

        for i in range(n_classes):
            plt.plot(
                fpr[i],
                tpr[i],
                color=get_colors_per_class(i)[2][0],
                lw=2,
                label='ROC curve of class {0} (area = {1:0.2f})'
                ''.format(i, roc_auc[i])
            )

        plt.plot([0, 1], [0, 1], 'k--', lw=2)
        plt.xlim([-0.025, 1.025])
        plt.ylim([-0.05, 1.05])
        plt.grid(alpha=.2)
        plt.xlabel('False Positive Rate (Fall-out)')
        plt.ylabel('True Positive Rate (Recall)')
        plt.title('Multi-Class (non-threshold-aware) extension of Receiver Operating Characteristic (ROC)')
        plt.legend(loc="lower right")
        plt.show()

    if show and in_ipynb() and n_classes == 2:
        # PLOT ROC Derivates and Threshold/Recall curves
        def plot_roc_analysis(fpr, tpr, thr):
            def xyd(x, y, nbs):
                d = {}
                for n in nbs:
                    x = np.linspace(0, 1, n, endpoint=True)
                    y = np.interp(x, fpr, tpr)
                    d.update({n: (x, y)})
                return d

            def df(x, y):
                _, ix = np.unique(x, return_index=True)
                x, y = x[ix], y[ix]
                return (x[1:] + x[:-1]) / 2, (y[1:] - y[:-1]) / (x[1:] - x[:-1])

            def dfd(xy_d):
                return {n: df(*args) for n, args in xy_d.items()}

            xy_d = xyd(fpr, tpr, reversed([10, 25, 50]))
            xy1_d = dfd(xy_d)
            xy2_d = dfd(xy1_d)

            plt.figure(figsize=(19.5, 5.5))

            # Derivates
            plt.subplot(1, 2, 1)
            for n, (x, y) in xy1_d.items():
                plt.plot(x, y, label=f'dROC n={n}')
            plt.plot([0, 1], [1, 1], label='1')
            plt.ylabel('First Derivative')
            plt.legend(loc='right')
            plt.grid(alpha=.2)
            plt.xticks(np.arange(0, 1 + 1e-10, .1))
            ax2 = plt.gca().twinx()
            for n, (x, y) in xy2_d.items():
                ax2.plot(x, y, '--', label=f'ROC\'\' (n={n})')
            plt.ylabel('Second Derivative (dotted)')
            plt.xticks(np.arange(0, 1 + 1e-10, .1))
            plt.grid(alpha=.2)
            plt.title('ROC Derivatives')

            # Recall curves
            plt.subplot(1, 2, 2)
            plt.plot(thr[1:], tpr[1:], label='Recall 1')
            plt.plot(thr[1:], 1 - fpr[1:], label='Recall 0')
            plt.xlabel('Threshold (probability)')
            plt.ylabel('Recall')
            plt.yticks(np.arange(0, 1 + 1e-10, .1))
            plt.xticks(np.arange(0, 1 + 1e-10, .1))
            plt.legend()
            plt.grid(alpha=.2)
            plt.title('Threshold / Recall Curves')
            plt.show()

        plot_roc_analysis(fpr[1], tpr[1], thr[1])

        # Plot CALIBRATION CURVE
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true,
            y_pred_proba[:, 1],
            n_bins=int(min(30, max(10, round(y_true.shape[0] / 100)))),
        )
        plt.figure(figsize=(8, 4))
        plt.plot(
            [0, 1],
            [0, 1],
            "k:",
            label="Perfectly calibrated",
        )
        plt.plot(
            mean_predicted_value,
            fraction_of_positives,
            "s-",
            label="Calibration Curve",
        )
        plt.xlabel('Mean predicted value')
        plt.ylabel('Fraction of positives')

        plt.title("Calibration curve")
        plt.grid(alpha=.2)
        plt.show()

    return {
        'per_class':
            {
                i: {
                    'class_roc_area': roc_auc[i],
                    'class_FPR': fpr[i].mean(),
                    'class_TPR': tpr[i].mean()
                }
                for i in range(n_classes)
            },
        'total':
            {
                'macro_roc_area': roc_auc["macro"],
                'micro_roc_area': roc_auc["micro"],
                'macro_FPR': fpr["macro"].mean(),
                'micro_FPR': fpr["micro"].mean(),
                'macro_TPR': tpr["macro"].mean(),
                'micro_TPR': tpr["micro"].mean(),
                'n_classes': n_classes
            }
    }


def join_ml_results(*args, show=True):
    results = {'per_class': defaultdict(dict), 'total': {}}
    # Inputs are multiple dictionaries
    if len(args) >= 1 and isinstance(args[0], dict):
        iters = args
    # Input is a list of dictionaries
    elif len(args) == 1 and isinstance(args[0], list):
        iters = args[0]
    else:
        raise Exception('Pass ml_results dictionaries as a list or as multiple arguments')

    for arg in iters:
        assert isinstance(arg, dict)
        if 'per_class' in arg:
            for class_id, class_dict in arg['per_class'].items():
                for key, value in class_dict.items():
                    results['per_class'][class_id][key] = value
        if 'total' in arg:
            for key, value in arg['total'].items():
                results['total'][key] = arg['total'][key] = value

    if show:
        show_results_dataframe(results)

    return results


# def recall_keras(y_true, y_pred):
#         true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
#         possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
#         recall = true_positives / (possible_positives + K.epsilon())
#         return recall

# def precision_keras(y_true, y_pred):
#         true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
#         predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
#         precision = true_positives / (predicted_positives + K.epsilon())
#         return precision
