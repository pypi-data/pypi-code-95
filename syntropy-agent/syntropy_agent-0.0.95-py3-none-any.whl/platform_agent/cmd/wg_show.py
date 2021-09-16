import subprocess
import re


def get_wg_listen_port(ifname):
    """Gets wg interface port"""
    wg_show_proc = subprocess.Popen(['wg', 'show', ifname], stdout=subprocess.PIPE)
    grep_proc = subprocess.Popen(['grep', 'listening port'], encoding='utf-8', stdout=subprocess.PIPE, stdin=wg_show_proc.stdout)

    listen_port_text = grep_proc.stdout.read()
    x = re.findall('[0-9]+', listen_port_text)
    if x:
        return x[0]
