import os
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pwd_path = os.path.abspath(os.path.dirname(__file__))

filenames = {
    'mozilla': 'lines.10k.cfo.sample.2000 - Mozilla (Firefox, Core, OS).csv',
    'kubernetes': 'lines.10k.cfo.sample.2000 - Kubernetes (Slackarchive.io).csv',
    'lucene': 'lines.10k.cfo.sample.2000 - Lucene-dev mailing list.csv',
    'bitcoin': 'lines.10k.cfo.sample.2000 - Bitcoin (github.com).csv'
}

category_dict = {1: 'NL', 2: 'CODE', 3: 'TRACE',
                 4: 'LOG', 5: 'NL_CODE', 6: 'NL_TRACE', 7: 'NL_LOG'}


def get_category_dict():
    return category_dict


def loadDataFromFiles():
    X = []
    y = []
    for source, filename in filenames.items():
        data = pd.read_csv(os.path.join(pwd_path, filename),
                           header=0, encoding="UTF-8")
        data.insert(0, 'Source', source, True)
        if source == 'lucene':
            data['Text'] = list(map(lambda text: re.sub(
                r'^[>\s]+', '', text), data['Text']))
        X.extend(data['Text'])
        y.extend(data['Class'])
        data['Class'] = data['Class'].map(category_dict)
        data.to_csv(path_or_buf=os.path.join(pwd_path, f'{source}.csv'), columns=[
                    'Source', 'Text', 'Class'], index=False)
    return X, np.asarray(y)


def loadStopWords():
    stop_words_file = os.path.join(pwd_path, 'mysql_sw_wo_code_words.txt')
    stop_words = pd.read_csv(stop_words_file, header=None)
    return stop_words[0].values.tolist()


def plotDistribution():
    df = pd.DataFrame()
    results = dict()
    category_names = ['NL', 'CODE', 'TRACE', 'LOG',
                      'NL_CODE', 'NL_TRACE', 'NL_LOG']
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(0.15, 0.85, 7))
    for source, filename in filenames.items():
        df[source] = pd.read_csv(os.path.join(pwd_path, source)+'.csv',
                                 header=0, encoding="UTF-8", usecols=['Class'])
        results[source] = [(df[source] == x).sum() for x in category_names]
    print(results)
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max() + 10)
    fig.suptitle('Distribution for each data source')

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=0.7,
                        label=colname, color=color)
        ax.bar_label(rects, label_type='center',
                     color='black', fontsize='small')
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='medium')
    plt.show()
    plt.savefig(f'Distribution_each_source.png')
