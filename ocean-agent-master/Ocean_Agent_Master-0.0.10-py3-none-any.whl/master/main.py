# master setup 실행한 다음 자동으로 서버를 system service로 등록하기
import logging

import click

from master import utils
from master.cmd.setup import setup as master_setup
from master.cmd.setup import setup_calico as master_setup_calico
from master.cmd.setup import setup_system_service as master_setup_system_service
from master.cmd.serve import serve as master_serve
from master.cmd.serve import PORT

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


@click.group()
def cli():
    pass


@cli.command()
@click.option("--nic", help="(Optional) Network interface card to communicate with workers. Default to first NIC (e.g. eth0)", type=click.STRING, required=False)
@click.option("--pod-cidr", help="(Optional) Pod CIDR for kubernetes. Default to 192.168.0.0/16", type=click.STRING, required=False)
@click.option("--calico-only", help="(Optional) Install calico only. Can be used with --pod-cidr", is_flag=True, required=False)
def setup(nic, pod_cidr, calico_only):
    if calico_only:
        master_setup_calico(pod_cidr=pod_cidr)
    if not utils.check_kubeadm_initialized():
        if master_setup(nic):
            master_setup_calico(pod_cidr=pod_cidr)
            master_setup_system_service()

    logging.info(f"""\n
    Run below command in all worker servers.
    > agent-worker join --master-endpoint={utils.get_api_server_address(nic)}:{PORT}
    """)


@cli.command()
def serve():
    master_serve()


if __name__ == "__main__":
    cli()
