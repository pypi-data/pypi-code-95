from zipline.data.bundles import register

from fsharadar.ingest import ingest_bundle

from fsharadar.daily.meta import (
    bundle_name,
    bundle_tags,
)

@register(bundle_name, create_writers=True)
def ingest_daily():
    pass

def ingest(tickers_file, data_file, show_progress=False):

    tickers_table = 'SF1'
    actions_file = None

    ingest_bundle(bundle_name,
                  bundle_tags,
                  tickers_table,
                  tickers_file,
                  data_file,
                  actions_file,
                  show_progress)
