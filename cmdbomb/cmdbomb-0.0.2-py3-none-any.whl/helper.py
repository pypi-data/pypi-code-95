def get_key(d, val):
    for key, value in d.items():
         if val == value:
             return key
    return None
