from hashlib import md5
import os
import pickle
import glob

def dir_content_cache_(dir, pattern="*"):
    fl = glob.glob(dir + "/" + pattern)
    s = ''.join(fl)
    key = "key_"+dir
    return fl, s,key

def cache_contains_dir(cache_base, dir, pattern="*"):
    # fl = glob.glob(dir)
    fl,s,key =  dir_content_cache_(dir, pattern=pattern)

    v = [cache_contains_file(cache_base, f) for f in fl]
    if all(v) and cache_contains_str(cache_base, key, s):
        return True
    return False

def cache_update_dir(cache_base, dir, pattern="*"):
    fl, s, key = dir_content_cache_(dir, pattern=pattern)
    cache_update_str(cache_base, key, s)
    for f in fl:
        cache_update_file(cache_base, f)


def cache_contains_str(cache_base,key=None,value=None):
    assert(key or value)
    value = hash_binary_(value.encode())
    if not key: key = value
    return cache_contains_hash(cache_base, key, value)

def cache_update_str(cache_base,key,value):
    assert(key or value)
    value = hash_binary_(value.encode())
    if not key: key = value
    return cache_update_hash(cache_base, key, value)


def cache_contains_file(cache_base,file):
    key = os.path.abspath(file)
    if not os.path.exists(file):
        return False
    value = hash_file_(file)
    return cache_contains_hash(cache_base, key, value)

def hash_file_(file):
    import hashlib
    hasher = hashlib.md5()
    with open(file, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def cache_update_file(cache_base, file):
    key = os.path.abspath(file)
    value = hash_file_(file)
    return cache_update_hash(cache_base, key, value)


def cache_contains_hash(cache_base,key,hash_val):
    cc = load_cache(cache_base)
    return cc.get(key,"Not found") == hash_val

def cache_update_hash(cache_base,key,hash_val):
    cc = load_cache(cache_base)
    cc[key] = hash_val
    save_cache(cache_base, cc)


def hash_binary_(str_bin):
    return md5(str_bin).hexdigest()


def cache_file(cache_base):
    return os.path.join(cache_base, "cache.pkl")

def save_cache(cache_base, cache):
    with open(cache_file(cache_base), 'wb') as f:
        pickle.dump(cache,f)

def load_cache(cache_base):
    if not os.path.exists(cache_file(cache_base)):
        save_cache(cache_base, {'default' : 42})
        return load_cache(cache_base)
    with open(cache_file(cache_base), 'rb') as f:
        return pickle.load(f)


if __name__ == "__main__":
    cache_base = "./"

    print("Hello World")
