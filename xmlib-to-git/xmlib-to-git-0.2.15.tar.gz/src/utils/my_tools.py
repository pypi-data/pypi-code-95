import re


def mysplit(string, max=None):
    s = re.sub("((?![\w]).)", "_", string)  # supression des charactères spéciaux
    s = re.sub("([_-]+)", "_", s)  # suppression des répétitions de undersocre et tiret
    s = s.rstrip("_").rstrip("-")
    if max: # réduire la taille de la chaine de caractère si on défini un max
        s = s[:max] + '~' if len(s) > max else s
    return s


