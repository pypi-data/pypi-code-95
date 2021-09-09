#!/usr/bin/env python

from datetime import datetime
import base64
import getpass
import json
import logging
import os
import re
import requests
import shutil
import subprocess
import sys

from edgebox import edgebox_os

RESERVED_CLOUDLET_ORGS = ( "edgebox", "mobiledgex" )
DEF_CONSOLE = "console.mobiledgex.net"
DOCKER_CONFIG = os.path.expanduser("~/.docker/config.json")

def prompt(text, default=None, choices=None, validate=None):
    prompt_str = text
    if choices:
        choices = [str(x) for x in choices]
        prompt_str += " (one of: " + ", ".join(choices) + ")"
    if default and (not choices or default in choices):
        prompt_str += " (\"{0}\")".format(default)
    else:
        # Invalid default; ignore
        default = None
    prompt_str += ": "

    reply = None
    while not reply:
        reply = input(prompt_str).strip()
        if not reply:
            if default:
                reply = default
            else:
                continue
        if choices and reply not in choices:
            print("Not a valid choice: {0}".format(reply))
            reply = None
        elif validate:
            vresp = validate(reply)
            if not vresp:
                reply = None

    return reply

def validate_float(string, min_val, max_val):
    if not string:
        return True
    try:
        val = float(string)
    except ValueError:
        print("Not a valid float")
        return False

    if val < min_val or val > max_val:
        print("Value not within bounds [{0},{1}]".format(min_val, max_val))
        return False

    return True

class McApiException(Exception):
    def __init__(self, message, status_code=-1):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return "[{0}] {1}".format(self.status_code, self.message)

class MC(dict):

    class PasswordStore:
        ENVIRONMENT = 1
        MACOS_KEYCHAIN = 2

    CONSOLE_USERNAME_ENV = ""
    CONSOLE_PASSWORD_ENV = "MOBILEDGEX_CONSOLE_PASSWORD"

    def __init__(self, name, varsfile):
        self.name = name
        self.varsfile = varsfile
        self.params = {}
        self._password = None
        self._password_store = None
        self._token = None
        self._regions = None
        self._orgs = None
        self._flavors = None
        self._roles = None
        self._location_defaults = None
        self._location_name = None
        self.revalidate = False
        self.artf_username = None
        self.artf_password = None
        self._docker_logged_in = None
        self.need_cloudlet_org = False

        if os.path.exists(varsfile):
            with open(varsfile, "r") as f:
                self.params = json.load(f)

        for p in self.params:
            if self.params[p] == "UNSET":
                self.params[p] = None

        if 'darwin' in sys.platform:
            self._os = edgebox_os.MacOS(self)
        else:
            # Assume Linux
            self._os = edgebox_os.Linux(self)

    def _revalidate(self, key):
        default = self.params.get(key)
        if self.revalidate != False and key not in self.revalidate:
            self.params[key] = None
            self.revalidate.add(key)
        return default

    @property
    def host(self):
        key = "mc"
        default = self._revalidate(key)
        if not default:
            default = DEF_CONSOLE
        if key not in self.params or not self.params[key]:
            self.params[key] = prompt("Console Host", default=default)
            if self.params[key] != default:
                # Reset computed parameters
                for p in ("controller", "deploy-env", "region"):
                    self.params[p] = None
                self._regions = self._orgs = self._roles = None
                self._password = self._token = None

        return self.params[key]

    @property
    def docker(self):
        if self.deploy_env == "main":
            return "docker.mobiledgex.net"
        return "docker-{}.mobiledgex.net".format(self.deploy_env)

    @property
    def docker_running(self):
        with open(os.devnull, "w") as devnull:
            rc = subprocess.call(["docker", "info"],
                                 stdout=devnull,
                                 stderr=devnull)
            return True if rc == 0 else False

    @property
    def docker_logged_in(self):
        if self._docker_logged_in is None:
            self._docker_logged_in = self._os.docker_logged_in
        return self._docker_logged_in

    @property
    def username(self):
        key = "user"
        default = self._revalidate(key)
        if not default:
            default = getpass.getuser()
        if key not in self.params or not self.params[key]:
            logging.debug("Looking up username in env: " + MC.CONSOLE_USERNAME_ENV)
            u = os.environ.get(MC.CONSOLE_USERNAME_ENV)
            if not u:
                u = prompt("Console username for {}".format(self.host), default)
            self.params[key] = u
        return self.params[key]

    @property
    def password(self):
        if not self._password:
            self._password = self._os.password
            if not self._password:
                logging.debug("Looking for password in env: " + MC.CONSOLE_PASSWORD_ENV)
                self._password = os.environ.get(MC.CONSOLE_PASSWORD_ENV)
                self._password_store = MC.PasswordStore.ENVIRONMENT
            if not self._password:
                self._password = getpass.getpass(prompt="Console password for {}: ".format(
                    self.host))
                self._os.password = self._password
        return self._password

    @property
    def username_sanitized(self):
        return re.sub(r"[^\d\w]", "-", self.username)

    @property
    def default_edgebox_operator(self):
        return "edgebox-{}-org".format(self.username_sanitized)

    def create_default_cloudlet_org(self):
        name = self.default_edgebox_operator
        self.call("org/create", data={
            "name": name,
            "type": "operator",
        })

    def activate(self):
        self.params["active"] = "yes"

    def deactivate(self):
        self.params["active"] = "no"

    @property
    def is_active(self):
        value = self.params.get("active", "yes")
        return value == "yes"

    @property
    def token(self):
        if self._token:
            # Check if token is valid
            try:
                self.call("user/current", token=self._token)
            except Exception as e:
                # Token invalid
                logging.debug("Token has expired; fetching a new one")
                self._token = None

        if not self._token:
            try:
                r = requests.post("https://{0}/api/v1/login".format(self.host),
                              json={"username": self.username, "password": self.password})
                self._token = r.json()["token"]
            except Exception as e:
                print("ERROR: Failed to log in to MC \"{0}\" as user \"{1}\"".format(
                    self.host, self.username), file=sys.stderr)
                print("Deleting stored passwords (if any)")
                del self._os.password
                if os.environ.get(MC.CONSOLE_PASSWORD_ENV):
                    print("Please make sure the password in the environment is valid: {}".format(
                        MC.CONSOLE_PASSWORD_ENV), file=sys.stderr)
                sys.exit(3)

        return self._token

    def call(self, api, method="POST", timeout=180, token=None, data={}, **kwargs):
        if not data:
            data = kwargs
        if not token:
            token = self.token
        headers = {
            "Accept": "application/json",
            "Authorization": "Bearer " + token,
        }
        r = requests.request(method, "https://{0}/api/v1/auth/{1}".format(
                                        self.host, api),
                             headers=headers,
                             json=data,
                             timeout=timeout)
        logging.debug("Response: {0}".format(r.text))
        if r.status_code != requests.codes.ok:
            raise McApiException("API call failed: {0}: {1} {2}".format(
                api, r.status_code, r.text), r.status_code)

        def load_json(text):
            d = json.loads(text)
            if len(d) == 1 and 'data' in d:
                d = [ d["data"] ]
            return d

        resp = []
        if r.text:
            try:
                resp = load_json(r.text)
            except Exception as e:
                # Check if response is a JSON stream
                try:
                    for line in r.text.splitlines():
                        resp.extend(load_json(line))
                except Exception:
                    # Throw the original exception
                    raise e
        return resp

    @property
    def regions(self):
        if not self._regions:
            self._regions = {}
            for ctrl in self.call("controller/show"):
                self._regions[ctrl["Region"]] = ctrl["Address"]
        return self._regions

    @property
    def orgs(self):
        if not self._orgs:
            self._orgs = {}
            for org in self.call("org/show"):
                self._orgs[org["Name"]] = org["Type"]
        return self._orgs

    @property
    def flavors(self):
        if not self._flavors:
            self._flavors = {}
            for flavor in self.call("ctrl/ShowFlavor",
                                    data={
                                        "region": self.region,
                                    }):
                self._flavors[flavor["key"]["name"]] = flavor
        return self._flavors

    @property
    def roles(self):
        if not self._roles:
            self._roles = self.call("role/assignment/show")
        return self._roles

    @property
    def location_defaults(self):
        """Use IP geolocation to determine defaults for lat-long"""
        if not self._location_defaults:
            try:
                r = requests.get("http://ipinfo.io/geo", timeout=2)
                self._location_defaults = r.json()
            except Exception as e:
                self._location_defaults = {}
        return self._location_defaults

    @property
    def location_name(self):
        if not self._location_name:
            locdefs = self.location_defaults
            self._location_name = "{0}, {1}".format(locdefs["city"], locdefs["country"])
        return self._location_name

    @property
    def latitude(self):
        key = "latitude"
        default = self._revalidate(key)
        if not self.params[key]:
            prompt_str = "Latitude"
            if not default:
                locdefs = self.location_defaults
                if "loc" in locdefs:
                    latlong = locdefs["loc"].split(',')
                    default = latlong[0]
                else:
                    default = "33.01"
            self.params[key] = prompt(prompt_str, default,
                                      validate=lambda x: validate_float(x, -90, 90))
            self.params[key] = float(self.params[key])
        return self.params[key]

    @property
    def longitude(self):
        key = "longitude"
        default = self._revalidate(key)
        if not self.params[key]:
            prompt_str = "Longitude"
            if not default:
                locdefs = self.location_defaults
                if "loc" in locdefs:
                    latlong = locdefs["loc"].split(',')
                    default = latlong[1]
                else:
                    default = "-96.61"
            self.params[key] = prompt(prompt_str, default,
                                      validate=lambda x: validate_float(x, -180, 180))
            self.params[key] = float(self.params[key])
        return self.params[key]

    @property
    def region(self):
        key = "region"
        default = self._revalidate(key)
        if key not in self.params or not self.params[key]:
            self.params[key] = prompt("Region", choices=sorted(self.regions.keys()),
                                      default=default)
            self.params["controller"] = None
        return self.params[key]

    @property
    def controller(self):
        key = "controller"
        self._revalidate(key)
        if key not in self.params or not self.params[key]:
            self.params[key] = self.regions[self.region].split(":")[0]
        return self.params[key]

    @property
    def cloudlet(self):
        key = "cloudlet"
        default = self._revalidate(key)
        if key not in self.params or not self.params[key]:
            if not default:
                default = "edgebox-" + self.username_sanitized
            self.params[key] = prompt("Cloudlet", default=default)
        return self.params[key]

    @property
    def cloudlet_pool(self):
        poolname = re.sub(r'-org$', '', self.cloudlet_org.lower())
        prefix = "edgebox-" + self.username_sanitized + "-"
        if not (poolname + "-").startswith(prefix):
            poolname = prefix + poolname
        poolname += "-pool"
        return poolname

    def validate_org(self, org):
        if org.lower() in RESERVED_CLOUDLET_ORGS:
            print("{0} is a reserved org. Please pick another.".format(org))
            return False
        if org not in self.orgs:
            print("Org does not exist or is not accessible: {0}".format(org))
            return False
        if self.orgs[org] != "operator":
            print("Not an operator org: {0}".format(org))
            return False

        for r in self.roles:
            if r["org"] == org and r["username"] == self.username \
                    and r["role"] == "OperatorManager":
                # Valid role
                return True

        print("User \"{0}\" not OperatorManager in org \"{1}\"".format(
            self.username, org))
        return False

    @property
    def cloudlet_org(self):
        key = "cloudlet-org"
        default = self._revalidate(key)
        if default and default not in self.orgs:
            logging.debug("Default org not accessible: {}".format(default))
            default = None
        if key not in self.params or not self.params[key]:
            orgs = [x for x in self.orgs.keys() if self.orgs[x] == "operator"]
            def_org = self.default_edgebox_operator
            if orgs:
                # Pick the default edgebox operator org, if available
                if not default and def_org in orgs:
                    default = def_org
                self.params[key] = prompt("Cloudlet Org", choices=sorted(orgs),
                                          validate=lambda x: self.validate_org(x),
                                          default=default)
            else:
                # Create a new operator org
                self.params[key] = def_org
                self.need_cloudlet_org = True

        return self.params[key]

    @property
    def deploy_env(self):
        key = "deploy-env"
        default = self._revalidate(key)
        if key not in self.params or not self.params[key]:
            m = re.match(r'console([^\.]*)\.', self.host)
            if not m:
                raise Exception("Unable to determine vault address for MC: " + self.host)
            d = m.group(1)
            self.params[key] = d.lstrip("-") if d else "main"
        return self.params[key]

    @property
    def logdir(self):
        return os.path.join("/var/tmp", "edgebox-{0}".format(self.name))

    @property
    def confdir(self):
        return os.path.dirname(self.varsfile)

    def create_cloudlet(self):
        r = self.call("ctrl/CreateCloudlet",
                      data={
                          "cloudlet": {
                              "crm_override": 4, # IgnoreCrmAndTransientState
                              "flavor": {
                                  "name": "x1.medium",
                              },
                              "ip_support": 2, # IpSupportDynamic
                              "key": {
                                  "name": self.cloudlet,
                                  "organization": self.cloudlet_org,
                              },
                              "location": {
                                  "latitude": self.latitude,
                                  "longitude": self.longitude,
                              },
                              "num_dynamic_ips": 254,
                              "platform_type": 5,
                          },
                          "region": self.region,
                      })
        return r

    def get_access_key(self):
        r = self.call("ctrl/GenerateAccessKey",
                      data={
                          "cloudletkey": {
                              "name": self.cloudlet,
                              "organization": self.cloudlet_org,
                          },
                          "region": self.region,
                      })
        return r["message"]

    def get_cloudlet(self):
        return self.call("ctrl/ShowCloudlet",
                         data={
                             "cloudlet": {
                                 "key": {
                                     "name": self.cloudlet,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                             "region": self.region,
                         })

    def get_cloudlet_info(self):
        return self.call("ctrl/ShowCloudletInfo",
                         data={
                             "cloudletinfo": {
                                 "key": {
                                     "name": self.cloudlet,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                             "region": self.region,
                         })

    def get_cluster_instances(self, with_real_names=False):
        clusters = {}
        real_cluster_names = {}
        for appinst in self.call("ctrl/ShowAppInst",
                                 data={
                                     "appinst": {
                                         "key": {
                                             "cluster_inst_key": {
                                                 "cloudlet_key": {
                                                     "name": self.cloudlet,
                                                     "organization": self.cloudlet_org,
                                                 },
                                             },
                                         },
                                     },
                                     "region": self.region,
                                 }):
            cluster_key = appinst["key"]["cluster_inst_key"]
            cluster = {"key": cluster_key}

            real_cluster_name = appinst.get("real_cluster_name")
            if real_cluster_name:
                real_cluster_names[real_cluster_name] = cluster_key
                if with_real_names:
                    cluster["_real_name"] = real_cluster_name

            dict_key = json.dumps(cluster_key, sort_keys=True)
            clusters[json.dumps(cluster_key, sort_keys=True)] = cluster

        clusters = list(clusters.values())

        for clustinst in self.call("ctrl/ShowClusterInst",
                                   data={
                                       "clusterinst": {
                                           "key": {
                                               "cloudlet_key": {
                                                   "name": self.cloudlet,
                                                   "organization": self.cloudlet_org,
                                               },
                                           },
                                       },
                                       "region": self.region,
                                   }):
            cluster_name = clustinst["key"]["cluster_key"]["name"]
            if cluster_name not in real_cluster_names and not clustinst.get("reservable", False):
                clusters.append(clustinst)

        return clusters

    def get_app_instances(self, cluster, cluster_org):
        return self.call("ctrl/ShowAppInst",
                         data={
                             "appinst": {
                                 "key": {
                                     "cluster_inst_key": {
                                         "cloudlet_key": {
                                             "name": self.cloudlet,
                                             "organization": self.cloudlet_org,
                                         },
                                         "cluster_key": {
                                             "name": cluster,
                                         },
                                         "organization": cluster_org,
                                     },
                                 },
                             },
                             "region": self.region,
                         })

    def delete_app_instance(self, cluster, cluster_org, app_name, app_org, app_vers, force=True):
        data = {
            "appinst": {
                "key": {
                    "app_key": {
                        "name": app_name,
                        "organization": app_org,
                        "version": app_vers,
                    },
                    "cluster_inst_key": {
                        "cloudlet_key": {
                            "name": self.cloudlet,
                            "organization": self.cloudlet_org,
                        },
                        "cluster_key": {
                            "name": cluster,
                        },
                        "organization": cluster_org,
                    },
                },
            },
            "region": self.region,
        }

        resp = {}
        try:
            resp = self.call("ctrl/DeleteAppInst", data=data)
        except McApiException as e:
            if e.status_code == 400 and "not ready" in e.message:
                logging.debug("{0}: Attempting force delete".format(e.message))
                data["appinst"]["crm_override"] = 2
                resp = self.call("ctrl/DeleteAppInst", data=data)
            else:
                raise e

        return resp

    def delete_cluster_instance(self, cluster, cluster_org):
        data = {
            "clusterinst": {
                "key": {
                    "cloudlet_key": {
                        "name": self.cloudlet,
                        "organization": self.cloudlet_org,
                    },
                    "cluster_key": {
                        "name": cluster,
                    },
                    "organization": cluster_org,
                }
            },
            "region": self.region,
        }

        resp = {}
        try:
            resp = self.call("ctrl/DeleteClusterInst", data=data)
        except McApiException as e:
            if e.status_code == 403 and "Forbidden" in e.message:
                logging.debug("{0}: skipping delete".format(e.message))
            elif e.status_code == 400 and "not ready" in e.message:
                logging.debug("{0}: Attempting force delete".format(e.message))
                data["clusterinst"]["crm_override"] = 2
                resp = self.call("ctrl/DeleteClusterInst", data=data)
            else:
                raise e

        return resp

    def delete_cloudlet(self):
        return self.call("ctrl/DeleteCloudlet",
                         data={
                             "cloudlet": {
                                 "key": {
                                     "name": self.cloudlet,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                             "region": self.region,
                         }, timeout=10)

    def get_cloudlet_pool(self):
        return self.call("ctrl/ShowCloudletPool",
                         data={
                             "region": self.region,
                             "cloudletpool": {
                                 "key": {
                                     "name": self.cloudlet_pool,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                         })

    def create_cloudlet_pool(self):
        return self.call("ctrl/CreateCloudletPool",
                         data={
                             "region": self.region,
                             "cloudletpool": {
                                 "key": {
                                     "name": self.cloudlet_pool,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                         })

    def add_cloudlet_to_pool(self):
        return self.call("ctrl/AddCloudletPoolMember",
                         data={
                             "region": self.region,
                             "cloudletpoolmember": {
                                 "key": {
                                     "name": self.cloudlet_pool,
                                     "organization": self.cloudlet_org,
                                 },
                                 "cloudlet_name": self.cloudlet,
                             },
                         })

    def get_cloudlet_pool_invitations(self, org=None):
        data = {
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
        }
        if org:
            data["org"] = org
        return self.call("cloudletpoolaccessinvitation/show", data=data)

    def create_cloudlet_pool_invitation(self, org):
        return self.call("cloudletpoolaccessinvitation/create", data={
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
            "org": org,
        })

    def delete_cloudlet_pool_invitation(self, org):
        return self.call("cloudletpoolaccessinvitation/delete", data={
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
            "org": org,
        })

    def get_cloudlet_pool_response(self, org=None, decision=None):
        data = {
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
        }
        if org:
            data["org"] = org

        resp = self.call("cloudletpoolaccessresponse/show", data=data)
        if decision:
            logging.debug("Filtering cloudlet pool responses for decision={}".format(
                decision))
            resp = [ x for x in resp if x["Decision"] == decision ]

        return resp

    def create_cloudlet_pool_response(self, org, decision="accept"):
        return self.call("cloudletpoolaccessresponse/create", data={
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
            "org": org,
            "decision": decision,
        })

    def delete_cloudlet_pool_response(self, org):
        return self.call("cloudletpoolaccessresponse/delete", data={
            "cloudletpool": self.cloudlet_pool,
            "cloudletpoolorg": self.cloudlet_org,
            "region": self.region,
            "org": org,
        })

    def link_org_to_pool(self, org):
        logging.debug("Checking if invite already present: {}".format(org))
        invite = self.get_cloudlet_pool_invitations(org)
        if not invite:
            logging.debug("Creating cloudlet pool invite: {}".format(org))
            self.create_cloudlet_pool_invitation(org)

        logging.debug("Checking if invite is already accepted: {}".format(org))
        resp = self.get_cloudlet_pool_response(org)
        if resp:
            if resp[0]["Decision"] != "accept":
                raise Exception("Cloudlet pool invitation in rejected state")
        else:
            logging.debug("Accepting cloudlet pool invite: {}".format(org))
            resp = self.create_cloudlet_pool_response(org)

        return resp

    def unlink_org_from_pool(self,org):
        logging.debug("Revoking cloudlet pool acceptance: {}".format(org))
        try:
            self.delete_cloudlet_pool_response(org)
        except Exception as e:
            logging.debug("Failed to revoke pool acceptance: {}".format(e))

        logging.debug("Revoking cloudlet pool invite: {}".format(org))
        try:
            self.delete_cloudlet_pool_invitation(org)
        except Exception as e:
            logging.debug("Failed to revoke pool invitation: {}".format(e))

    def show_cloudlet_pool_orgs(self, org=None):
        return self.get_cloudlet_pool_response(decision="accept")

    def delete_cloudlet_pool(self):
        return self.call("ctrl/DeleteCloudletPool",
                         data={
                             "region": self.region,
                             "cloudletpool": {
                                 "key": {
                                     "name": self.cloudlet_pool,
                                     "organization": self.cloudlet_org,
                                 },
                             },
                         })

    def validate(self):
        self.revalidate = set()
        for param in ("host", "region", "cloudlet_org", "cloudlet", "latitude",
                      "longitude"):
            getattr(self, param)
        self.revalidate = False

    def save(self):
        # Load all computed parameters
        for p in ("host", "controller", "region", "deploy_env", "cloudlet",
                  "cloudlet_org", "latitude", "longitude"):
            getattr(self, p)

        if os.path.exists(self.varsfile):
            # Back up existing vars file
            bakfile = self.varsfile + "." \
                + datetime.now().strftime("%Y-%m-%d-%H%M%S")
            shutil.copy(self.varsfile, bakfile)

        params = self.params.copy()
        for p in params:
            if not params[p]:
                params[p] = "UNSET"

        with open(self.varsfile, "w") as f:
            json.dump(params, f, indent=4, sort_keys=True)

    def banner(self, msg):
        print("\n*** {} ***".format(msg))

    def confirm_continue(self, prompt="Continue?"):
        while True:
            reply = input(prompt + " (yn) ").lower().strip()
            if reply.startswith("y"):
                return True
            if reply.startswith("n"):
                return False

    def __str__(self):
        cloudlet_org = self.params["cloudlet-org"]
        if self.need_cloudlet_org:
            cloudlet_org += " (create new)"
        return """    MC: {mc}
    Region: {region}
    Cloudlet Org: {cloudlet_org}
    Cloudlet: {cloudlet}
    Cloudlet Pool: {cloudlet_pool}
    Latitude: {latitude}
    Longitude: {longitude}
    Output Dir: {outputdir}
""".format(**self.params,
           cloudlet_org=cloudlet_org,
           cloudlet_pool=self.cloudlet_pool,
           outputdir=self.logdir)
