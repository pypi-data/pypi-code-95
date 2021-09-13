#!/usr/bin/python

from __future__ import absolute_import, print_function

from lazr.restful.wsgi import WSGIApplication

if __name__ == '__main__':
    import sys
    host, port = sys.argv[1:3]
    server = WSGIApplication.make_server(
        host, port, 'lazr.restful.example.wsgi')
    server.handle_request()
