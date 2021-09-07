def init(key):
    import os
    from string import Template
    url = "https://app.community.saturnenterprise.io"
    set_url = "export SATURN_BASE_URL='{}' > /dev/null 2>&1".format(url)
    set_api = "export SATURN_TOKEN='{}' > /dev/null 2>&1".format(key)
    os.system(set_url)
    os.system(set_api)

def start(key):
    init(key)
    import joblib
    from dask_saturn import SaturnCluster
    from dask.distributed import Client
    cluster = SaturnCluster()
    client = Client(cluster)


def run(function):
    with joblib.parallel_backend("dask"):
        function()
