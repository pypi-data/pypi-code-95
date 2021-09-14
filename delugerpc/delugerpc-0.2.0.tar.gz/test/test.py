import delugerpc
import time


magnet = "magnet:?xt=urn:btih:64a980abe6e448226bb930ba061592e44c3781a1&dn=ubuntu-21.04-desktop-amd64.iso"
client = delugerpc.deluge_rpc_api(secured=True, host="192.168.8.8")
option = {
    "download_location": "/mnt/X/TD/test",
    "stop_ratio": 0,
    "add_paused": False,
}
print(client.auth.login("deluge"))
print(client.core.add_torrent_magnet(
    uri=magnet,
    options=option
))
time.sleep(20)
print(client.core.remove_torrent(
    torrent_id=magnet.split(":btih:")[-1].split("&")[0],
    remove_data=True
))


# update core.py (RPC methods) from the deluge python library
# you may need to extract plugin egg files to directory with their corresponding egg file name
# import delugerpc.utils
# delugerpc.utils.generate_core(r"C:\Program Files\Python39\lib\site-packages\deluge")
