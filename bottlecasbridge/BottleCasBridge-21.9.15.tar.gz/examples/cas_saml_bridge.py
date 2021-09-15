import os
from bottle import Bottle
from BottleSessions import BottleSessions, Backing
from BottleSaml import SamlSP
from BottleCasBridge import CasBridge

from sample_config import saml_config, session_config, cas_config

DEBUG = os.environ.get('DEBUG', False)

r = Backing(**session_config['session_backing'])
del session_config['session_backing']

app = Bottle()

BottleSessions(app, session_backing=r, **session_config)
saml = SamlSP(app, saml_config)

CasBridge(app, saml, cas_config, r, saml.log)

if DEBUG:
    import json
    from bottle import request, static_file, response
    @app.route('/sess')
    def sess():
        response.set_header('content-type','text/plain')
        return json.dumps(request.session, indent=4)
    
    @app.route('/assets/<path:path>')
    def assets(path):
        return static_file(path, root='./assets/')

if __name__ == '__main__':
    app.run(port=8000, debug=DEBUG, reloader=DEBUG)
else:
    application = app
