import json
import pydantic
from . import funtions


class nets(pydantic.BaseModel):
    cidr: str
    name: str
    handle: str
    iprange: str
    description: str
    country: str
    state: str
    city: str
    address: str
    postal_code: int
    emails: list
    created: str
    updated: str


class lookup(pydantic.BaseModel):
    asn_registry: str
    asn: int
    asn_cidr: str
    asn_country_code: str
    asn_date: str
    asn_description: str
    query: str
    nets: list
    cidr: str = ''
    name: str = ''
    handle: str = ''
    iprange: str = ''
    description: str = ''
    country: str = ''
    state: str = ''
    city: str = ''
    address: str = ''
    postal_code: int = 0
    emails: list = []
    created: str = ''
    updated: str = ''


class whois:
    def __init__(self, ip):
        self.ip: str = ip
        self.rvjson: dict = funtions.whois(self.ip)

        obj: lookup = lookup(**self.rvjson)

        obj.nets[0]['iprange'] = obj.nets[0]['range']
        del obj.nets[0]['range']
        obj.nets = nets(**obj.nets[0])

        self.obj = obj
        self.asn_registry: str = obj.asn_registry
        self.asn: int = obj.asn
        self.asn_cidr: str = obj.asn_cidr
        self.asn_country_code: str = obj.asn_country_code
        self.asn_date: str = obj.asn_date
        self.asn_description: str = obj.asn_description
        self.cidr: str = obj.nets.cidr
        self.name: str = obj.nets.name
        self.handle: str = obj.nets.handle
        self.iprange: str = obj.nets.iprange
        self.description: str = obj.nets.description
        self.country: str = obj.nets.country
        self.state: str = obj.nets.state
        self.city: str = obj.nets.city
        self.address: str = obj.nets.address
        self.postal_code: int = obj.nets.postal_code
        self.emails: list = obj.nets.emails
        self.created: str = obj.nets.created
        self.updated: str = obj.nets.updated

    def json(self):
        return json.dumps(self.rvjson, indent=3)

    @staticmethod
    def info():
        return funtions.who_is_info()
