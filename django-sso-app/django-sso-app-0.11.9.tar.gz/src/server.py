import os

import cherrypy

from django_sso_app.config.wsgi import application

SOCKET_FILE = '/tmp/app.sock'
CHERRYPY_THREAD_POOL_SIZE = os.environ.get('CHERRYPY_THREAD_POOL_SIZE', 30)
CHERRYPY_SOCKET_HOST = os.environ.get('CHERRYPY_SOCKET_HOST', '0.0.0.0')
CHERRYPY_SOCKET_PORT = os.environ.get('CHERRYPY_SOCKET_PORT', 5000)


def run(host=CHERRYPY_SOCKET_HOST, port=CHERRYPY_SOCKET_PORT):
    # Cleanup socket file
    try:
        os.remove(SOCKET_FILE)
    except OSError:
        pass

    # Mount the application
    cherrypy.tree.graft(application, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = host
    server.socket_port = port
    server.thread_pool = CHERRYPY_THREAD_POOL_SIZE

    # If in same node use socket files
    # https://lists.freebsd.org/pipermail/freebsd-performance/2005-February/001143.html
    server.socket_file = SOCKET_FILE

    # For SSL Support
    # server.ssl_module            = 'pyopenssl'
    # server.ssl_certificate       = 'ssl/certificate.crt'
    # server.ssl_private_key       = 'ssl/private.key'
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Example for a 2nd server (same steps as above):
    # Remember to use a different port

    # server2             = cherrypy._cpserver.Server()

    # server2.socket_host = "0.0.0.0"
    # server2.socket_port = 8081
    # server2.thread_pool = 30
    # server2.subscribe()

    # Start the server engine (Option 1 *and* 2)

    cherrypy.engine.start()

    # change socket permissions
    os.chmod(SOCKET_FILE, 0o777)

    cherrypy.engine.block()


if __name__ == '__main__':
    run()
