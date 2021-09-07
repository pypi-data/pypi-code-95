import time
from tqdm import tqdm

from zipline.utils.context_tricks import CallbackManager

# Optionally show a progress bar for the given iterator.
# tqdm-based version of click-based maybe_show_progress in zipline.utils.cli

def maybe_show_progress(it, show_progress, **kwargs):
    
    if show_progress:
        return tqdm(it, **kwargs)

    # context manager that just return `it` when we enter it
    return CallbackManager(lambda it=it: it)

def print_progress(memo, t1):
    t2 = time.perf_counter()
    if t1 is not None: print('Processing time: {:0.4f} seconds'.format(t2-t1))
    print('\n', memo, sep='')
    return t2
