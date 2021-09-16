import os
import compress_pickle
# __version__ = "0.0.1"

def cache_write(object, file_name, verbose=True):
    dn = os.path.dirname(file_name)
    if not os.path.exists(dn):
        os.mkdir(dn)
    if verbose: print("Writing cache...", file_name)
    with open(file_name, 'wb', ) as f:
        compress_pickle.dump(object, f, compression="lzma")
    if verbose: print("Done!")


def cache_exists(file_name):
    # file_name = cn_(file_name) if cache_prefix else file_name
    return os.path.exists(file_name)


def cache_read(file_name):
    # file_name = cn_(file_name) if cache_prefix else file_name
    if os.path.exists(file_name):
        with open(file_name, 'rb') as f:
            return compress_pickle.load(f, compression="lzma")
            # return pickle.load(f)
    else:
        return None

