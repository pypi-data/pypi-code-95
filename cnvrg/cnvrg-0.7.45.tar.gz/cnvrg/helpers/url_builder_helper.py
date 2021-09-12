import re


def __clean_start_end_slashes(s):
    if s.endswith("/"): s = s[:-1]
    if s.startswith("/"): s = s[1:]
    return s


def url_join(path, *paths):
    all_paths = [path] + list(paths)
    joined_url = "/".join(map(__clean_start_end_slashes, filter(lambda x: x, all_paths)))
    return re.sub(r'[\/]{2,}', "/", joined_url).replace("http:/", "http://").replace("https:/", "https://")
