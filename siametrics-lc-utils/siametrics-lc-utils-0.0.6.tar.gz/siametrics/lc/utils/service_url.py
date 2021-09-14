import os
from dns.resolver import resolve


def resolve_srv(url):
    answers = resolve(url, 'SRV')
    record = answers[0]
    host = record.target.to_text().rstrip('.')
    port = record.port
    a_url = f'http://{host}:{port}'
    return a_url


def srv_record(name, type_):
    def wrapper(self: 'ServiceUrl'):
        if type_ == 'srv':
            return resolve_srv(f'{name}.lc-{self.environment}')
        raise NotImplementedError()

    return property(wrapper)


class ServiceUrl:
    def __init__(self, environment):
        self.environment = environment

    matching = srv_record('matching-service', 'srv')
    tms = srv_record('tms-service', 'srv')
    location = srv_record('location-service', 'srv')
    pricing = srv_record('pricing-service', 'srv'),


service_url = ServiceUrl(os.environ.get('ENVIRONMENT', 'dev'))
