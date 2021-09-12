from typing import List, Callable, Dict
from cnvrg.helpers.env_helper import POOL_SIZE
import types
from multiprocessing.pool import Pool
from tqdm import tqdm

def safe_parallel(func: Callable, list, pool_size: int = POOL_SIZE, progressbar: Dict=None):
    """
    safe parallel function, it support
    :param func: function to execute every time
    :param list: generator or list
    :param pool_size: how much processes will work
    :param progressbar: tqdm paramteres (if passing generator, total is mendatory (if you want progressbar)
    :return:
    """
    results = []
    pbar = None
    if not isinstance(list, types.GeneratorType):
        gen = generator_wrap(list)
    else:
        gen = list
    with Pool(processes=pool_size) as pool:
        try:
            if progressbar:
                pbar = tqdm(**progressbar)
            for batch in gen:
                for res in pool.imap_unordered(func, batch):
                    if progressbar:
                        pbar.update()
                    results.append(res)
        except Exception as e:
            raise e
        finally:
            pool.close()
            try:
                if pbar: pbar.close()
            except Exception as e:
                pass
        return results


def generator_wrap(llist: List, chunks_size: int=None):
    llist = list(llist)
    chunks_size = chunks_size or 10000
    for i in range(0, len(llist), chunks_size):
        yield llist[i:i+chunks_size]
