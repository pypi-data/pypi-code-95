import aria2rpc


url = "http://www.google.com"
token = "SECRET"
client = aria2rpc.aria2_rpc_api(host="192.168.5.5", secret=token)
urls = [url]
option = {
    "dir": "/home/su/Downloads/test",
    "out": "test.html",
}
print(client.addUri(
    uris=urls,
    options=option,
))


# update core.py (RPC methods) from the latest aria2 docs
# import aria2rpc.utils
# aria2rpc.utils.generate_core()
