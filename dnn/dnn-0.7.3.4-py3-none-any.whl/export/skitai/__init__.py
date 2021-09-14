
def __setup__ (pref):
    try:
        pref.config.tf_models
    except AttributeError:
        raise AssertionError ("need pref.config.tf_models")
