import os
import json
import uuid
import munch
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from mako.lookup import TemplateLookup

apiname = os.environ.get('SOLACE_API_NAME', str(uuid.uuid4()))

# TODO: raise our own custom error types
def objectify(dict):
    return munch.munchify(dict)

class SolaceResponse(Response):
    json = munch.munchify({})
    html = None

    def __init__(self, config = {}):
        super().__init__()
        self.config = config
        self.lookup = TemplateLookup(
            directories=[self.config.get("templates_dir", "src/templates")], 
            module_directory=self.config.get("modules_dir", "src/modules")
        )

    def tpl(self, template, context = {}):
        template = self.lookup.get_template(template)
        self.html = template.render(**context)

class Solace:
    def __init__(self, config = {}):
        self.cors = None
        self.config = munch.munchify(config)
        self.rules = Map([])
        self.views = {}
    
    def __rule(self, method, urlpath, handler):
        uid = str(uuid.uuid4())
        self.rules.add(
            Rule(
                urlpath, 
                endpoint=uid,
                methods=[method]
            )
        )
        self.views[uid] = handler

    def get(self, urlpath, handler):
        """
        The GET method requests a representation of the 
        specified resource. Requests using GET should only 
        retrieve data.
        """
        self.__rule('GET', urlpath, handler)

    def head(self, urlpath, handler):
        """
        The HEAD method asks for a response identical to that
        of a GET request, but without the response body.
        """
        self.__rule('HEAD', urlpath, handler)

    def post(self, urlpath, handler):
        """
        The POST method is used to submit an entity to the 
        specified resource, often causing a change in state
        or side effects on the server.
        """
        self.__rule('POST', urlpath, handler)

    def put(self, urlpath, handler):
        """
        The PUT method replaces all current representations 
        of the target resource with the request payload.
        """
        self.__rule('PUT', urlpath, handler)

    def delete(self, urlpath, handler):
        """
        The DELETE method deletes the specified resource.
        """
        self.__rule('DELETE', urlpath, handler)

    def connect(self, urlpath, handler):
        """
        The CONNECT method establishes a tunnel to the server 
        identified by the target resource.
        """
        self.__rule('CONNECT', urlpath, handler)

    def options(self, urlpath, handler):
        """
        The OPTIONS method is used to describe the communication
        options for the target resource.
        """
        self.__rule('OPTIONS', urlpath, handler)

    def trace(self, urlpath, handler):
        """
        The TRACE method performs a message loop-back test along 
        the path to the target resource.
        """
        self.__rule('TRACE', urlpath, handler)

    def patch(self, urlpath, handler):
        """
        The PATCH method is used to apply partial modifications
        to a resource.
        """
        self.__rule('PATCH', urlpath, handler)

    # def register(self, Middleware):
    #     pass

    # def __next_func(self, handler):
    #     handler(self.req, self.res, self.__next_func)

    def __dispatch(self, req):
        adapter = self.rules.bind_to_environ(req.environ)
        self.req = req
        self.res = SolaceResponse()
        try:
            endpoint, values = adapter.match()
            self.req.params = munch.munchify(values)
            if endpoint not in self.views:
                raise NotFound

            # NOTE: this defines the signature for all request handlers...
            self.views[endpoint](self.req, self.res)

            # Enables CORS Support
            if self.cors is not None:
                for header in self.cors:
                    self.res.headers.set(header, self.cors.get(header))

            if self.res.json:
                self.res.content_type = "application/json"
                self.res.data = json.dumps(self.res.json)
                return self.res

            if self.res.html:
                self.res.content_type = "text/html"
                self.res.data = self.res.html
                return self.res

            return self.res
        except HTTPException as e:
            # TODO: offer an optional HTML error page to avoid showing JSON errors.
            err = {
                'code': e.code,
                'message': e.description
            }
            res = Response(json.dumps({"error": err}), e.code)
            res.content_type = 'application/json'
            return res 

    def __wsgi_app(self, environ, start_response):
        req = Request(environ)
        res = self.__dispatch(req)
        return res(environ, start_response)

    def __call__(self, environ, start_response):
        return self.__wsgi_app(environ, start_response)

class DevelopmentServer:
    
    # TODO: look at more configuration options 
    # that we can support for the DevelopmentServer.
    # https://werkzeug.palletsprojects.com/en/2.0.x/serving/

    def __init__(self, app, host = "127.0.0.1", port = 5000, reload = True):
        self.app = app
        self.host = host
        self.port = port
        self.reload = reload
    
    def start(self):
        run_simple(
            self.host, 
            self.port, 
            self.app, 
            use_debugger=False,
            use_reloader=self.reload
        )
