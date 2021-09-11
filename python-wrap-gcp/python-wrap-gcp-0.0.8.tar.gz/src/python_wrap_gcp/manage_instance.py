import subprocess, inspect, re, socket, memcache, json
from threading import Thread
import pandas as pd
from python_wrap_gcp.misc.helpers import log
from python_wrap_gcp.docs.config import MemcachedConfig, GCPConfig


def stdout_to_frame(stdout):
    l = [re.split(r"\s{2,13}", r) for r in stdout.decode('utf-8').split("\n")]
    schema = [col.strip() for col in l[0] if len(col.strip()) > 2]
    return pd.DataFrame([row for row in l if len(row) == len(schema)], columns=schema)


def list_gcp_instances(by, **kwargs):
    out = subprocess.Popen(['gcloud', 'compute', 'instances', 'list',
                            '--filter', kwargs.get('prefix', GCPConfig.WORKER_PREFIX)],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()
    frame = stdout_to_frame(stdout)
    if 'condition' in kwargs:
        frame = frame[frame[by] == kwargs['condition']]
    return frame


def match_ip_to_zone(ip):
    frame = list_gcp_instances('')
    d = frame.set_index('EXTERNAL_IP').ZONE.to_dict()
    return d[ip]


def manage_gcp_instance(*args, action='start', by='EXTERNAL_IP', **kwargs):
    """
    Start or stop VM by identifier
    :param args:
    :param action: str, `start`, `stop`
    :param by: str, `EXTERNAL_IP`, `INTERNAL_IP`, `ZONE`
    :param kwargs:
        :param prefix: str, prefix VM's to apply action
    :return: np.array, internal and external IP of affected VM's
    """
    def wrap_gcloud_action(names, zone):
        out = subprocess.Popen(['gcloud', 'compute', 'instances', action, '--zone', zone] + names,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        instance_names = ','.join(names)
        log(inspect.stack(), f"{action}: {zone}: {instance_names}", "I")

        return stdout

    frame = list_gcp_instances(by, **kwargs)
    gcloud_jobs = [[zone, df.NAME.tolist()] for zone, df in frame.groupby('ZONE')]
    if len(gcloud_jobs) == 0:
        raise AssertionError("no matching instances")
    for zone, names in gcloud_jobs:
        thread = Thread(target=wrap_gcloud_action, args=(names, zone))
        thread.start()
    if action == 'start':
        internal_ip = frame.INTERNAL_IP.values[0]
        frame = list_gcp_instances('INTERNAL_IP', **{**kwargs,
                                                     **{'condition': internal_ip}})
    return frame[['INTERNAL_IP', 'EXTERNAL_IP']].values


def get_host_ip(local=False):
    if local:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    else:
        import urllib.request
        try:
            ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        except:
            ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
    return ip


def request_restart(source_name):
    mc = memcache.Client([f"{MemcachedConfig.HOST}:{MemcachedConfig.PORT}"], debug=0)
    ip = get_host_ip()
    cache = mc.get(GCPConfig.RESTART_KEY)
    if cache is None:
        cache = {ip: (source_name, 0, 'false')}
    else:
        cache = json.loads(cache)
        if ip in cache:
            restart_count = int(cache[ip][1]) + 1
            if restart_count > GCPConfig.MAX_INSTANCE_RESTART:
                return
            cache[ip] = source_name, str(restart_count), 'false'
        else:
            cache[ip] = source_name, 0, 'false'
    print(json.dumps(cache))
    mc.set(GCPConfig.RESTART_KEY, json.dumps(cache), time=GCPConfig.RESTART_TTL)  # restart done by master
    log(inspect.stack(), f"{json.dumps(cache)}", "I")
    mc.set(f"{source_name},{ip}", 'true', time=GCPConfig.IP_BLOCK_SECONDS)  # blocked IP quarantine


def restart_until_valid_ip(mc, external_ip, source_name):
    """
    Rotate VM with a blocked external IP per source name until new is assigned
    :param external_ip:
    :param source_name:
    :param max_restart:
    :return:
    """
    max_restart = GCPConfig.MAX_INSTANCE_IP_RESTART
    zone = match_ip_to_zone(external_ip)
    while max_restart > 0:
        internal, _ = manage_gcp_instance(action="stop", by='EXTERNAL_IP', condition=external_ip,
                                          zone=zone)[0]
        # assumed only one IP matched
        _, external_ip = manage_gcp_instance(action="start", by='INTERNAL_IP', condition=internal,
                                             zone=zone)[0]
        cache = mc.get(f"{source_name},{external_ip}")
        if cache is None:
            log(inspect.stack(), f"assigned external IP: {external_ip} for internal: {internal}", "I")
            return True
        else:
            max_restart -= 1
            log(inspect.stack(), f"already seen: {external_ip}, retry left: {max_restart}", "W")
    internal, _ = manage_gcp_instance(action="stop", by='INTERNAL_IP', condition=internal)[0]
    log(inspect.stack(), f"failed IP replacement for {external_ip}, turned off VM {internal}", "E")
    return False


def perform_restart(*args, **kwargs):
    mc = memcache.Client([f"{MemcachedConfig.HOST}:{MemcachedConfig.PORT}"], debug=0)
    cache = json.loads(mc.get(GCPConfig.RESTART_KEY))
    any_action_taken = False
    for external_ip, (source_name, restart_count, was_performed) in cache.items():
        if was_performed == 'true':
            continue
        any_action_taken = restart_until_valid_ip(mc, external_ip, source_name)

    if any_action_taken:  # update only if new requests
        mc.set(GCPConfig.RESTART_KEY, json.dumps({ip: (source_name, count, 'true')
                                                  for ip, (source_name, count, _) in cache.items()}),
               time=GCPConfig.RESTART_TTL)  # flag as done
