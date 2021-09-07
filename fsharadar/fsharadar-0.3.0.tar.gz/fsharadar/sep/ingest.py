from zipline.data.bundles import register

from fsharadar.ingest import ingest_bundle

from fsharadar.sep.meta import (
    bundle_name,
    bundle_tags,
)

@register(bundle_name, create_writers=True)
def ingest_sep():
    pass

def ingest(tickers_file,
           data_file,
           actions_file,
           show_progress=False): 

    ingest_bundle(bundle_name,
                  bundle_tags,
                  'SEP', # bundle_tickers_table
                  tickers_file,
                  data_file,
                  actions_file,
                  show_progress)




 
