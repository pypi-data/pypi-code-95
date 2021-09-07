from fsharadar.load import load_bundle
from fsharadar.sfp.meta import bundle_name, bundle_tags

def load():
    return load_bundle(bundle_name, bundle_tags, adjustment=True)
