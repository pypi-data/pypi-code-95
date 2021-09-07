# -*- coding: utf-8 -*-
"""
    pip_services3_rpc.rest.SimpleServer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Simple WSGI web server with shutdown hook
    from http://stackoverflow.com/questions/11282218/bottle-web-framework-how-to-stop
    
    :copyright: Conceptual Vision Consulting LLC 2018-2019, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

import ssl

from bottle import ServerAdapter
from cheroot import wsgi
from cheroot.ssl.builtin import BuiltinSSLAdapter


class SSLCherryPyServer(ServerAdapter):
    server = None

    def run(self, handler):
        self.server = wsgi.Server((self.host, self.port), handler)

        certfile = self.options.pop('certfile', None)
        keyfile = self.options.pop('keyfile', None)

        if certfile and keyfile:
            self.server.ssl_adapter = BuiltinSSLAdapter(certfile, keyfile)

            # By default, the server will allow negotiations with extremely old protocols
            # that are susceptible to attacks, so we only allow TLSv1.2
            self.server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1
            self.server.ssl_adapter.context.options |= ssl.OP_NO_TLSv1_1

        try:
            self.server.start()
        finally:
            if self.server:
                self.server.stop()

    def shutdown(self):
        if self.server:
            self.server.stop()
            self.server = None
