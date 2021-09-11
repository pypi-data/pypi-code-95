import logging

from master.server import server
from master import utils
from apscheduler.schedulers.background import BackgroundScheduler

HOST = "0.0.0.0"
PORT = "8080"

HARBOR_SVC_FQDN = "harbor.harbor.svc.cluster.local."
HARBOR_SVC = "harbor.harbor.svc"


def serve():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(lambda: utils.set_host_from_kubernetes_dns(HARBOR_SVC, HARBOR_SVC_FQDN), 'interval', minutes=5)
    sched.start()
    logging.info("Starting host sync..")

    server.run(host=HOST, port=PORT)