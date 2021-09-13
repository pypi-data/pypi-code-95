from xmlrpc.client import ServerProxy


__ALL__ = ["aria2_rpc_api", "system_rpc_api"]


class base_rpc_api:
    def __init__(self, host: str = "127.0.0.1", port: int = 6800, secret: str = ""):
        self.secret = "token:{}".format(secret)
        self.client = ServerProxy("http://{}:{}/rpc".format(host, port))
        

class aria2_rpc_api(base_rpc_api):
    def addUri(self, secret=None, uris=None or list(), options=None or dict(), position=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.addUri
        if not uris:
            raise Exception("'uris' argument is required")
        params = [_ for _ in [secret or self.secret, uris, options, position] if _]
        return self.client.aria2.addUri(*params)

    def addTorrent(self, secret=None, torrent=None, uris=None or list(), options=None or dict(), position=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.addTorrent
        if not torrent:
            raise Exception("'torrent' argument is required")
        params = [_ for _ in [secret or self.secret, torrent, uris, options, position] if _]
        return self.client.aria2.addTorrent(*params)

    def addMetalink(self, secret=None, metalink=None, options=None or dict(), position=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.addMetalink
        if not metalink:
            raise Exception("'metalink' argument is required")
        params = [_ for _ in [secret or self.secret, metalink, options, position] if _]
        return self.client.aria2.addMetalink(*params)

    def remove(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.remove
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.remove(*params)

    def forceRemove(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.forceRemove
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.forceRemove(*params)

    def pause(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.pause
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.pause(*params)

    def pauseAll(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.pauseAll
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.pauseAll(*params)

    def forcePause(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.forcePause
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.forcePause(*params)

    def forcePauseAll(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.forcePauseAll
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.forcePauseAll(*params)

    def unpause(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.unpause
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.unpause(*params)

    def unpauseAll(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.unpauseAll
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.unpauseAll(*params)

    def tellStatus(self, secret=None, gid=None, keys=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellStatus
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid, keys] if _]
        return self.client.aria2.tellStatus(*params)

    def getUris(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getUris
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.getUris(*params)

    def getFiles(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getFiles
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.getFiles(*params)

    def getPeers(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getPeers
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.getPeers(*params)

    def getServers(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getServers
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.getServers(*params)

    def tellActive(self, secret=None, keys=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellActive
        params = [_ for _ in [secret or self.secret, keys] if _]
        return self.client.aria2.tellActive(*params)

    def tellWaiting(self, secret=None, offset=None, num=None, keys=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellWaiting
        if not offset:
            raise Exception("'offset' argument is required")
        if not num:
            raise Exception("'num' argument is required")
        params = [_ for _ in [secret or self.secret, offset, num, keys] if _]
        return self.client.aria2.tellWaiting(*params)

    def tellStopped(self, secret=None, offset=None, num=None, keys=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.tellStopped
        if not offset:
            raise Exception("'offset' argument is required")
        if not num:
            raise Exception("'num' argument is required")
        params = [_ for _ in [secret or self.secret, offset, num, keys] if _]
        return self.client.aria2.tellStopped(*params)

    def changePosition(self, secret=None, gid=None, pos=None, how=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.changePosition
        if not gid:
            raise Exception("'gid' argument is required")
        if not pos:
            raise Exception("'pos' argument is required")
        if not how:
            raise Exception("'how' argument is required")
        params = [_ for _ in [secret or self.secret, gid, pos, how] if _]
        return self.client.aria2.changePosition(*params)

    def changeUri(self, secret=None, gid=None, fileIndex=None, delUris=None, addUris=None, position=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.changeUri
        if not gid:
            raise Exception("'gid' argument is required")
        if not fileIndex:
            raise Exception("'fileIndex' argument is required")
        if not delUris:
            raise Exception("'delUris' argument is required")
        if not addUris:
            raise Exception("'addUris' argument is required")
        params = [_ for _ in [secret or self.secret, gid, fileIndex, delUris, addUris, position] if _]
        return self.client.aria2.changeUri(*params)

    def getOption(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getOption
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.getOption(*params)

    def changeOption(self, secret=None, gid=None, options=None or dict()):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.changeOption
        if not gid:
            raise Exception("'gid' argument is required")
        if not options:
            raise Exception("'options' argument is required")
        params = [_ for _ in [secret or self.secret, gid, options] if _]
        return self.client.aria2.changeOption(*params)

    def getGlobalOption(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getGlobalOption
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.getGlobalOption(*params)

    def changeGlobalOption(self, secret=None, options=None or dict()):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.changeGlobalOption
        if not options:
            raise Exception("'options' argument is required")
        params = [_ for _ in [secret or self.secret, options] if _]
        return self.client.aria2.changeGlobalOption(*params)

    def getGlobalStat(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getGlobalStat
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.getGlobalStat(*params)

    def purgeDownloadResult(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.purgeDownloadResult
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.purgeDownloadResult(*params)

    def removeDownloadResult(self, secret=None, gid=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.removeDownloadResult
        if not gid:
            raise Exception("'gid' argument is required")
        params = [_ for _ in [secret or self.secret, gid] if _]
        return self.client.aria2.removeDownloadResult(*params)

    def getVersion(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getVersion
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.getVersion(*params)

    def getSessionInfo(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.getSessionInfo
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.getSessionInfo(*params)

    def shutdown(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.shutdown
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.shutdown(*params)

    def forceShutdown(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.forceShutdown
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.forceShutdown(*params)

    def saveSession(self, secret=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#aria2.saveSession
        params = [_ for _ in [secret or self.secret] if _]
        return self.client.aria2.saveSession(*params)


class system_rpc_api(base_rpc_api):
    def multicall(self, methods=None):
        # https://aria2.github.io/manual/en/html/aria2c.html#system.multicall
        if not methods:
            raise Exception("'methods' argument is required")
        params = [_ for _ in [methods] if _]
        return self.client.system.multicall(*params)

    def listMethods(self):
        # https://aria2.github.io/manual/en/html/aria2c.html#system.listMethods
        params = [_ for _ in [] if _]
        return self.client.system.listMethods(*params)

    def listNotifications(self):
        # https://aria2.github.io/manual/en/html/aria2c.html#system.listNotifications
        params = [_ for _ in [] if _]
        return self.client.system.listNotifications(*params)

