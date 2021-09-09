#!/usr/bin/env python

import argparse
from datetime import datetime, timedelta
import getpass
import hashlib
import logging
import os
import requests
import shutil
import socket
from string import Template
import subprocess
import sys
import time

import edgebox
from edgebox import github
from edgebox.master_controller import MC, prompt, RESERVED_CLOUDLET_ORGS

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)

# Handle incompatibility between Pythons 2 and 3
try:
    input = raw_input
except NameError:
    pass

DEF_CONF_DIR = os.path.expanduser("~/.edgebox")
ARTF_BASE = "https://artifactory.mobiledgex.net/artifactory/edgebox-public"
RELEASE = "r3.0"
CONF_NAME = "config.json"
OS_DEPS = {
    "docker": "https://docs.docker.com/get-docker/",
    "helm": "https://helm.sh/docs/intro/install/",
    "sha1sum": {
        "darwin": "brew install md5sha1sum",
    },
    "wget": {
        "darwin": "brew install wget",
    },
}
BIN_DEPS = {
    "crmserver": 0o555,
    "dind-cluster-v1.14.sh": 0o555,
    "kubectl": 0o555,
    "mcctl": 0o555,
    "plugins/edgeevents.so": 0o444,
    "plugins/platforms.so": 0o444,
}
CLOUDLET_STATES = {
    1: "Not Present",
    2: "Create Requested",
    3: "Creating",
    4: "Create Error",
    5: "Ready",
    9: "Delete Requested",
    10: "Deleting",
    11: "Delete Error",
    13: "CRM Init OK",
    15: "Deleted",
}
CLOUDLETINFO_STATES = {
    0: "Unknown",
    1: "Errors",
    2: "Ready",
    3: "Offline",
    4: "Not Present",
    5: "Init",
    6: "Upgrade",
    7: "Needs Sync",
}

def init(args, name=None):
    confdir = os.path.join(args.confdir, (name or args.name))
    if not os.path.exists(confdir):
        os.makedirs(confdir)
    config = os.path.join(confdir, CONF_NAME)
    access_key_file = os.path.join(confdir, "accesskey.pem")

    os.environ["PATH"] = "/usr/local/bin:/usr/sbin:/sbin:/usr/bin:/bin"

    return config, access_key_file

def sha256sum(file):
    sha256 = hashlib.sha256()
    with open(file, "rb") as f:
        while True:
            data = f.read(65536)    # 64k buffer
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def download_artf(mc, path, deps_dir):
    if "darwin" in sys.platform:
        platform = "macos"
    else:
        platform = "linux"
    artf_url = os.path.join(ARTF_BASE, RELEASE, platform, path)
    username = mc.artf_username or mc.username
    password = mc.artf_password or mc.password
    r = requests.head(artf_url,
                      auth=(username, password))
    if r.status_code in (401, 403) and not mc.artf_username:
        username = prompt("Artifactory username")
        password = getpass.getpass(prompt="Artifactory password: ")
        r = requests.head(artf_url,
                          auth=(username, password))

    if r.status_code != requests.codes.ok:
        sys.exit("Error loading dependencies: {}".format(r.status_code))

    need_chksum = r.headers["X-Checksum-Sha256"]

    outfile = os.path.join(deps_dir, path)
    outdir = os.path.dirname(outfile)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    if os.path.exists(outfile):
        # Verify checksum
        file_chksum = sha256sum(outfile)
        if file_chksum != need_chksum:
            logging.debug("Checksum mismatch: {0} (not \"{1}\")".format(
                outfile, need_chksum))
            os.remove(outfile)

    if not os.path.exists(outfile):
        print("Downloading {}...".format(path))
        with requests.get(artf_url, auth=(username, password), stream=True) as r:
            r.raise_for_status()
            with open(outfile, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    assert sha256sum(outfile) == need_chksum, \
        "Checksum mismatch: {0}: not \"{1}\"".format( outfile, need_chksum)

    if not mc.artf_username:
        mc.artf_username = username
        mc.artf_password = password

def load_deps(mc, args, version):
    mc._os.register_service()
    deps_dir = os.path.join(args.confdir, "bin")
    if not os.path.exists(deps_dir):
        os.makedirs(deps_dir)
    deps_loaded = os.path.join(deps_dir, ".{}.done".format(edgebox.__version__))
    if not os.path.exists(deps_loaded):
        logging.debug("Loading dependencies")
        for file in sorted(BIN_DEPS.keys()):
            download_artf(mc, file, deps_dir)
            os.chmod(os.path.join(deps_dir, file), BIN_DEPS[file])

    deps_missing = False
    for binary in sorted(OS_DEPS.keys()):
        exe = shutil.which(binary)
        if not exe:
            deps_missing = True
            msg = "Missing dependency: \"{}\".".format(binary)
            if OS_DEPS[binary]:
                if isinstance(OS_DEPS[binary], dict):
                    if sys.platform in OS_DEPS[binary]:
                        msg += ' ("{}")'.format(OS_DEPS[binary][sys.platform])
                else:
                    msg += ' ("{}")'.format(OS_DEPS[binary])
            print(msg)

    if deps_missing:
        sys.exit()

    with open(deps_loaded, "a"):
        pass

    # Add deps path to system PATH
    os.environ["PATH"] = "{0}:{1}".format(deps_dir, os.environ["PATH"])
    os.environ["GOPATH"] = deps_dir

def create_cloudlet_org(mc):
    if not mc.need_cloudlet_org:
        logging.debug("Cloudlet org present: {}".format(mc.cloudlet_org))
        return

    mc.banner("Creating cloudlet org")
    mc.create_default_cloudlet_org()

def create_cloudlet_pool(mc):
    pool = mc.get_cloudlet_pool()
    if not pool:
        mc.banner("Creating cloudlet pool")
        mc.create_cloudlet_pool()

def delete_cloudlet_pool(mc):
    pool = mc.get_cloudlet_pool()
    if not pool:
        logging.debug("Cloudlet pool does not exist")
        return

    pool = pool[0]
    if "cloudlets" in pool and len(pool["cloudlets"]) > 0:
        logging.debug("Cloudlet pool not empty; skip deletion")
        return

    invites = mc.get_cloudlet_pool_invitations()
    if invites:
        logging.debug("Pending invitations in cloudlet pool: {}".format(
            invites))
        return

    mc.banner("Deleting cloudlet pool")
    mc.delete_cloudlet_pool()

def create_cloudlet(mc):
    mc.banner("Creating cloudlet")
    mc.create_cloudlet()

def add_cloudlet_to_pool(mc):
    mc.banner("Adding cloudlet to pool")
    try:
        mc.add_cloudlet_to_pool()
    except Exception as e:
        if "Cloudlet already part of pool" in str(e):
            print("Cloudlet already part of pool")
        else:
            raise e

def add_org_to_cloudlet_pool(mc, org):
    resp = mc.show_cloudlet_pool_orgs(org=org)
    if resp:
        if resp[0]["Decision"] != "accept":
            sys.exit("Sorry! Developer \"{org}\" has already rejected an "
                     "invitation to cloudlet pool \"{pool}\".\n"
                     "The rejection will need to be withdrawn to proceed "
                     "further.".format(
                         org=org, pool=mc.cloudlet_pool))
    else:
        mc.banner("Adding developer org to cloudlet pool")
        mc.link_org_to_pool(org)
        print()

def remove_orgs_from_cloudlet_pool(mc):
    for orgdet in mc.show_cloudlet_pool_orgs():
        org = orgdet["Org"]
        mc.banner("Removing developer org from cloudlet pool: {}".format(org))
        mc.unlink_org_from_pool(org)

def generate_access_key(mc, access_key_file):
    mc.banner("Generating access key")
    accesskey = mc.get_access_key()
    with open(access_key_file, "w+") as f:
        f.write(accesskey)
    return access_key_file

def get_notify_srv_port():
    for port in range(51001, 51100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                logging.debug("Port free: {}".format(port))
                break

                logging.debug("Port in use: {}".format(port))
                continue
    else:
        raise Exception("Unable to find free port for notify server")

    return str(port)

def start_crm(mc, access_key_file):
    mc.banner("Starting CRM")

    logdir = mc.logdir
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    outlog = os.path.join(logdir, "crm.out")
    errlog = os.path.join(logdir, "crm.log")

    if mc.deploy_env == "main":
        jaeger = "https://jaeger.mobiledgex.net:14268/api/traces"
    else:
        jaeger = "https://jaeger-{0}.mobiledgex.net:14268/api/traces".format(
            mc.deploy_env)
    os.environ["JAEGER_ENDPOINT"] = jaeger

    srv_port = get_notify_srv_port()
    logging.debug("Notify server port: {}".format(srv_port))

    crm_env = os.environ.copy()
    crm_env["MEX_EDGEBOX_DOCKER_USER"] = mc.username
    crm_env["MEX_EDGEBOX_DOCKER_PASS"] = mc.password

    cmd = [ "crmserver",
            "--notifyAddrs", mc.controller + ":37001",
            "--notifySrvAddr", "127.0.0.1:" + srv_port,
            "--cloudletKey",
            '{{"organization": "{0}","name":"{1}"}}'.format(mc.cloudlet_org, mc.cloudlet),
            "--hostname", "crm1",
            "--region", mc.region,
            "--platform", "PLATFORM_TYPE_EDGEBOX",
            "--useVaultPki",
            "--deploymentTag", mc.deploy_env,
            "--accessKeyFile", access_key_file,
            "--accessApiAddr", mc.controller + ":41001",
            "-d", "notify,infra,api,events" ]

    out = open(outlog, "w+")
    err = open(errlog, "w+")
    subprocess.Popen(cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
                     cwd=mc.logdir, start_new_session=True, env=crm_env)

def cleanup_cloudlet(mc):
    # Load user credentials
    mc.username
    mc.password

    for c in mc.get_cluster_instances(with_real_names=True):
        cluster = c["key"]["cluster_key"]["name"]
        cluster_org = c["key"]["organization"]
        real_name = c.pop("_real_name", None)

        for a in mc.get_app_instances(cluster, cluster_org):
            app_name = a["key"]["app_key"]["name"]
            app_vers = a["key"]["app_key"]["version"]
            app_org = a["key"]["app_key"]["organization"]

            mc.banner("Deleting app {0}@{1}".format(app_name, app_vers))
            mc.delete_app_instance(cluster, cluster_org, app_name, app_org, app_vers)

        cluster_name = real_name if real_name else cluster
        mc.banner("Deleting cluster {0}".format(cluster_name))
        try:
            mc.delete_cluster_instance(cluster_name, cluster_org)
        except Exception as e:
            if "not found" in str(e):
                print("Cluster does not exist")
            else:
                raise e

    mc.banner("Deleting cloudlet {0}".format(mc.cloudlet))
    try:
        mc.delete_cloudlet()
    except Exception as e:
        if "not found" in str(e):
            # Cloudlet has already been deleted
            print("Cloudlet does not exist")
        else:
            # Wait for cloudlet to be deleted
            start = datetime.now()
            while mc.get_cloudlet():
                logging.debug("Cloudlet still present; waiting...")
                if datetime.now() - start > timedelta(seconds=30):
                    # Failed to delete cloudlet
                    raise e
                time.sleep(2)

def get_crm_pid(mc, access_key_file):
    p = subprocess.Popen(["ps", "-eo", "pid,args"], stdout=subprocess.PIPE,
                         universal_newlines=True)
    out, err = p.communicate()
    for line in out.splitlines():
        (pid, args) = line.split(None, 1)
        if not args.startswith("crmserver "):
            continue
        if access_key_file not in args:
            continue
        return pid, args
    return None, None

def cleanup_crm(mc, access_key_file):
    pid, args = get_crm_pid(mc, access_key_file)
    if pid:
        mc.banner("Killing CRM process")
        logging.debug(args)
        subprocess.call(["kill", "-9", pid])

def cleanup_docker(mc):
    mc.banner("Cleaning up docker containers")
    comm = ["docker", "ps", "-a", "-q", "--filter", "label=cloudlet={0}".format(mc.cloudlet)]
    logging.debug("Containers: {0}".format(" ".join(comm)))
    p = subprocess.Popen(comm, stdout=subprocess.PIPE, universal_newlines=True)
    out, err = p.communicate()
    for container in out.splitlines():
        print("Deleting docker container " + container)
        subprocess.call(["docker", "stop", container])
        subprocess.call(["docker", "rm", container])

    mc.banner("Cleaning up docker networks")
    p = subprocess.Popen(["docker", "network", "list", "--format", "{{.Name}}"],
                         stdout=subprocess.PIPE, universal_newlines=True)
    out, err = p.communicate()
    for network in out.splitlines():
        if "kubeadm" in network:
            print("Deleting docker network " + network)

def is_cloudlet_ready(mc):
    try:
        info = mc.get_cloudlet_info()
    except Exception as e:
        logging.debug("Failed to fetch cloudlet info: {e}")
        info = None
    if info:
        logging.debug("Cloudlet status: {}".format(info))
        try:
            ready_state = [x for x in CLOUDLETINFO_STATES \
                             if CLOUDLETINFO_STATES[x] == "Ready"][0]
            return info[0]["state"] == ready_state
        except Exception:
            pass
    return False

def edgebox_create(args, mc=None, interactive=True):
    if mc is None:
        name = args.name
    else:
        name = mc.name

    config, access_key_file = init(args, name=name)

    if mc is None:
        mc = MC(name, config)

    if interactive and os.path.exists(config) and mc.is_active:
        print("Edgebox already active.")
        print("Do an \"edgebox delete {}\" first if you want to recreate it."\
              .format(mc.name))
        return 2

    if not mc.docker_running:
        print("Docker not running. Please start docker and try again.")
        return 2

    if interactive:
        mc.validate()
        mc.save()

    load_deps(mc, args, edgebox.__version__)
    if not mc.docker_logged_in:
        print("\nNot logged in to docker. Please run the following command:")
        print("  docker login -u {} {}".format(mc.username, mc.docker))
        return 2

    if interactive:
        if is_cloudlet_ready(mc):
            print("\nCloudlet already present: {} {} {}".format(
                mc.region, mc.cloudlet_org, mc.cloudlet))
            return 2

        print("\nCreating edgebox cloudlet:")
        print(mc)
        if not mc.confirm_continue():
            return "Not creating edgebox"

    mc.activate()
    mc.save()

    create_cloudlet_org(mc)
    create_cloudlet_pool(mc)
    create_cloudlet(mc)
    add_cloudlet_to_pool(mc)
    generate_access_key(mc, access_key_file)
    start_crm(mc, access_key_file)

    if interactive:
        print("Waiting for cloudlet to be ready...", end="", flush=True)
        count = 24
        while count > 0 and not is_cloudlet_ready(mc):
            count -= 1
            print(".", end="", flush=True)
            time.sleep(5)

        print("\n")
        if count > 0:
            print("Cloudlet is up")
        else:
            print("Error bringing up cloudlet")

def edgebox_delete(args):
    config, access_key_file = init(args)
    if not os.path.exists(config):
        return "Edgebox not found: {}".format(config)

    mc = MC(args.name, config)

    # Load user credentials
    mc.username
    mc.password

    print("\nDeleting edgebox cloudlet:")
    print(mc)
    if not mc.confirm_continue():
        return "Not deleting cloudlet"

    cleanup_cloudlet(mc)
    remove_orgs_from_cloudlet_pool(mc)
    delete_cloudlet_pool(mc)
    cleanup_docker(mc)
    cleanup_crm(mc, access_key_file)
    mc.deactivate()
    mc.save()

def edgebox_list(args):
    _, dirnames, _ = next(os.walk(args.confdir))
    fmt = "%-18s  %-22s  %-26s  %-8s"
    print(fmt % ("EDGEBOX", "CLOUDLET", "ORG", "STATUS"))
    print(fmt % ("-"*18, "-"*22, "-"*26, "-"*8))
    for dirname in sorted(dirnames):
        conffile = os.path.join(args.confdir, dirname, CONF_NAME)
        if os.path.exists(conffile):
            mc = MC(dirname, conffile)
            name = mc.name
            if mc.deploy_env != "main":
                name += " ({})".format(mc.deploy_env)
            print(fmt % (name, mc.cloudlet, mc.cloudlet_org,
                         "active" if mc.is_active else "inactive"))
   
def edgebox_show(args):
    config, _ = init(args)
    if not os.path.exists(config):
        return "Edgebox not found: {}".format(config)

    mc = MC(args.name, config)
    mc.username; mc.password
    print("\nEdgebox {}:".format(args.name))
    print(mc)

    cloudlet = mc.get_cloudlet()
    if not cloudlet:
        print("    Cloudlet not present")
        return

    errors = []

    cloudlet_state = cloudlet[0].get("state")
    errors.extend(cloudlet[0].get("errors", []))
    if cloudlet_state and cloudlet_state != 5:
        print("    Tracked State: {}".format(CLOUDLET_STATES.get(
            cloudlet_state, cloudlet_state)))

    info = mc.get_cloudlet_info()
    try:
        cloudletinfo_state = info[0]["state"]
        errors.extend(info[0].get("errors", []))
        print("    Cloudlet State: {}".format(CLOUDLETINFO_STATES.get(
            cloudletinfo_state, cloudletinfo_state)))
    except IndexError:
        print("    Cloudlet not ready")

    if errors:
        # Print out all unique error messages
        print("\n    Errors:\n      ", end="")
        print("\n      ".join(dict.fromkeys(errors).keys()))

def edgebox_github(args):
    config, _ = init(args)
    if not os.path.exists(config):
        return "Edgebox not found: {}".format(config)

    if not os.path.exists(os.path.join(args.repo, ".git")):
        return "Not a git repo: {}".format(args.repo)

    mc = MC(args.name, config)

    orgs = [x for x in mc.orgs.keys() if mc.orgs[x] == "developer" \
                          and x.lower() not in RESERVED_CLOUDLET_ORGS ]
    if not orgs:
        return "Not part of any developer orgs"

    org = prompt("Pick an org", choices=orgs, default=orgs[0])
    add_org_to_cloudlet_pool(mc, org)

    repo_conf_dir = os.path.join(args.repo, ".mobiledgex")
    if not os.path.exists(repo_conf_dir):
        os.makedirs(repo_conf_dir)

    repo_github_dir = os.path.join(args.repo, ".github/workflows")
    if not os.path.exists(repo_github_dir):
        os.makedirs(repo_github_dir)

    # Assume Github repo name is the app name
    app_name = os.path.basename(os.path.realpath(args.repo))

    data = {
        "appname": app_name,
        "devorg": org,
        "docker": mc.docker,
        "region": mc.region,
        "deployenv": mc.deploy_env,
        "flavor": None,
        "deployment": None,
        "ports": None,
        "cluster": None,
        "cloudlet": mc.cloudlet,
        "cloudletorg": mc.cloudlet_org,
    }

    workflow, data = github.load_workflow(data)
    app, data = github.load_app(data)
    appinst, data = github.load_appinst(data)

    flavors = mc.flavors.keys()
    data["flavor"] = prompt("Pick a flavor", choices=flavors, default=data["flavor"])
    data["deployment"] = data.get("deployment")
    # Prompt for deployment only if setting up the action for the first time
    if not data["deployment"]:
        data["deployment"] = prompt("Deployment type", choices=["kubernetes", "docker"],
                                default="kubernetes")
    data["ports"] = prompt("App ports [Eg: \"tcp:5678,tcp:9091,udp:9091\"]",
                           default=data["ports"])
    if not data["cluster"]:
        # Compute a cluster name
        data["cluster"] = "{}-cluster".format(app_name)
    data["cluster"] = prompt("Cluster name", default=data["cluster"])

    github.dump_workflow(workflow, data)
    github.dump_app(app, data)
    github.dump_appinst(appinst, data)

    print("""
Modify the following files as per your requirements, and add/commit them:
- .github/workflows/main.yml
- .mobiledgex/app.yml
- .mobiledgex/appinsts.yml

Make sure you have added your credentials for "{}" as Github secrets:
- MOBILEDGEX_USERNAME
- MOBILEDGEX_PASSWORD
See: https://docs.github.com/en/actions/reference/encrypted-secrets

Tag a release of your app.
""".format(mc.host))

def edgebox_startall(args, force=False):
    _, dirnames, _ = next(os.walk(args.confdir))
    edgeboxes = []

    def crm_startup(args, mc):
        # Check if cloudlet is up
        if is_cloudlet_ready(mc):
            # Nothing to do
            logging.debug("Edgebox already online: {}".format(mc.name))
            return None

        # Kill crmserver if it is running
        config, access_key_file = init(args, name=mc.name)
        cleanup_crm(mc, access_key_file)

        print("Starting edgebox \"{}\"".format(mc.name))
        edgebox_create(args, mc=mc, interactive=False)
        return mc

    for dirname in sorted(dirnames):
        conffile = os.path.join(args.confdir, dirname, CONF_NAME)
        if os.path.exists(conffile):
            mc = MC(dirname, conffile)
            mc.revalidate = False
            if mc.is_active:
                eb = crm_startup(args, mc)
                if eb is not None:
                    edgeboxes.append(eb)

    # Wait for all edgeboxes to come up
    count = 24
    while edgeboxes and count > 0:
        count -= 1
        logging.debug("CRMs starting up: {}".format(
                ", ".join([x.name for x in edgeboxes])))
        edgeboxes = [x for x in edgeboxes if not is_cloudlet_ready(x)]
        if edgeboxes:
            print("Waiting for edgebox(es): {}".format(
                ", ".join([x.name for x in edgeboxes])))
            time.sleep(5)
        else:
            break

    if edgeboxes:
        logging.error("Error starting edgebox(es): {}".format(
            ", ".join([x.name for x in edgeboxes])))

def edgebox_version(args):
    print("{} ({})".format(edgebox.__version__, RELEASE))

def main():
    parser = argparse.ArgumentParser(prog='edgebox',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--confdir", help="configuration directory",
                        default=DEF_CONF_DIR)
    subparsers = parser.add_subparsers(help="sub-command help", dest="cmd")
    subparsers.required = True

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("name", help="edgebox name")
    common_parser.add_argument("--region", help="region")
    common_parser.add_argument("--cloudlet", help="cloudlet name")
    common_parser.add_argument("--cloudlet-org", help="cloudlet org")

    parser_create = subparsers.add_parser("create", help="create edgeboxes",
                                          parents=[common_parser])
    parser_create.set_defaults(func=edgebox_create)

    parser_delete = subparsers.add_parser("delete", help="delete edgeboxes",
                                          parents=[common_parser])
    parser_delete.set_defaults(func=edgebox_delete)

    parser_list = subparsers.add_parser("list", help="list edgeboxes")
    parser_list.set_defaults(func=edgebox_list)

    parser_list = subparsers.add_parser("show", help="show edgebox details")
    parser_list.add_argument("name", help="edgebox name")
    parser_list.set_defaults(func=edgebox_show)

    parser_github = subparsers.add_parser("github", help="configure github actions")
    parser_github.add_argument("name", help="edgebox name")
    parser_github.add_argument("repo", help="github repo path", nargs="?", default=".")
    parser_github.set_defaults(func=edgebox_github)

    parser_start_all = subparsers.add_parser("startall", help="start all active edgeboxes")
    parser_start_all.set_defaults(func=edgebox_startall)

    parser_version = subparsers.add_parser("version", help="display version")
    parser_version.set_defaults(func=edgebox_version)

    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    sys.exit(args.func(args))

if __name__ == "__main__":
    main()
