import os
from collections import Counter

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt


def explore_data(arr, show_dist=True, title=None):
    """Get statistics on `arr`.
    
    get length/min/max/avg/25/50/75quantile/skew/kurtosis of `arr`
    
    if arr is a list of string, the min/max/avg/25/50/75quantile will 
    be not available.

    Args:
        arr (List): could be list of [int, float, str]
        show_dist (bool, optional): Whether to show distribution. 
            Defaults to True.
    """
    if not arr:
        return
    
    from_string = False
    
    if isinstance(arr[0], str):
        mapper = {}
        mapped_arr = []
        cnt = 0
        for i in arr:
            if i not in mapper:
                mapper[i] = cnt
                cnt += 1
            
            mapped_arr.append(mapper.get(i))
    
        arr = mapped_arr
        from_string = True
    
    if isinstance(arr[0], (int, float)):
        arr = np.array(arr)
        
        info = {
            "total": len(arr),
            "max": arr.max(),
            "min": arr.min(),
            "mean": arr.mean(),
            "25%": np.quantile(arr, 0.25), 
            "50%": np.quantile(arr, 0.5), 
            "75%": np.quantile(arr, 0.75),
            "skew": stats.skew(arr),  # 偏度
            "kurtosis": stats.kurtosis(arr),  # 峰度
        }
        
        for k, v in info.items():
            info[k] = round(v, 4)
            
            if k not in {"skew", "kurtosis", "total"} and from_string:
                info[k] = "-"  # drop meaningless info
        
        headline = "====== {} ======".format(title if title else "STAT")
        print(headline)
        for k, v in info.items():
            print(f" {k}: {v}")
        print("=" * len(headline) + "\n")

    if not show_dist:
        return
    
    sorted_counter = sorted(Counter(arr).items(), key=lambda x: x[1])
    x = [i[0] for i in sorted_counter]
    y = [i[1] for i in sorted_counter]

    plt.bar(x, y, color="orange")
    plt.title("Freq. Count")
    plt.show()


def explore_text(source, show_dist=False, title=None):
    """Describe a sequence of text.

    Given `source`, an iterable object of text, or a single text, or a path,
    read all lines from source, stats the length with explore_data(), then 
    get the count of unique tokens.
    
    Args:
        source (str, iterable): text source
        show_dist (bool, optional): if to show the length distribution. 
            Defaults to False.
        title (str, optional): title of the description. Defaults to None.

    Raises:
        TypeError: source should be a str object (a string), or a str filename
            of a text file, or a iterable object containing some strings.
            otherwise raises TypeError.
    """
    if isinstance(source, str):
        if os.path.exists(source):
            with open(source) as frd:
                source = frd.readlines()
        else:
            source = [source]

    elif not isinstance(source, (list, tuple)):
        raise TypeError(f"Unexpected input type:{type(source)}")

    length = []
    counter = Counter()
    
    for text in source:
        text = text.strip()
        length.append(len(text))
        counter.update(Counter(text))
    
    headline = "====== {} ======".format(title if title else "TEXT STAT")
    print(headline)
    print(f" vocab count: {len(counter)}")
    print(f" total lines: {len(length)}")
    print("=" * len(headline) + "\n")

    # stat the length info
    explore_data(length, show_dist=show_dist, title="LENGTH STAT")
