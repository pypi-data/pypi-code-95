import time
import click
import socket
import requests
import sched
from pyngrok import ngrok, conf


def duckdns_updater(port, protocol, token, domain):
    scheduler = sched.scheduler(time.time, time.sleep)
    for i in range(29200):
        scheduler.enter(
            60*60*6*i+2,
            1,
            update_target,
            kwargs={
                'port': port,
                'protocol': protocol,
                'token': token,
                'domain': domain
            }
        )


def update_target(port, protocol, token, domain):
    tunnel = ngrok.connect(addr=port, proto=protocol)
    print('Opened new tunnel at', tunnel.public_url)
    ip = socket.gethostbyname_ex(tunnel.public_url.split('://')[1].split('/')[0])[2]
    print('Pointing duckdns to', ip)
    resp = requests.get(
        "https://www.duckdns.org/update",
        params={
            'ip': ip,
            'domains': domain,
            'token': token
        }
    )
    print(resp.content)
    time.sleep(60*60*6)
    ngrok.disconnect(tunnel.public_url)


@click.command()
@click.argument('port', type=int, default=80)
@click.option('-d', '--duckdns-domain', required=True)
@click.option('-D', '--duckdns-token', required=True)
@click.option('-N', '--ngrok-token', required=False)
@click.option('-P', '--protocol', default='http')
@click.option('-R', '--region', default='en')
def cli(port, duckdns_domain, duckdns_token, ngrok_token=None, protocol=None, region=None):
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    if region:
        conf.get_default().region = region
    duckdns_updater(
        port,
        protocol,
        duckdns_token,
        duckdns_domain
    )
    while True:
        try:
            pass
        except KeyboardInterrupt:
            ngrok.get_ngrok_process().kill()
            exit(0)


if __name__ == '__main__':
    cli()
