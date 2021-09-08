from subprocess import check_output
import tornado.ioloop
import tornado.web
from tornado.escape import json_decode


class Runner:
    _app = None
    _script_path = None
    _port = None
    _inference_model = None

    def __init__(self, script_path, flags, port=80, inference_model=None):
        app = make_app()
        app.settings.update({'script_path': script_path, 'flags': flags})

        if inference_model is not None:
            raise "'inference_model' not supported now"

        self._port = port
        self._inference_model = inference_model
        self._app = app

    def run(self):
        print("Init app: ", self._port)
        self._app.listen(self._port)
        tornado.ioloop.IOLoop.current().start()


class InferHandler(tornado.web.RequestHandler):
    parsed_body = None

    def prepare(self):
        data = json_decode(self.request.body)

        if 'input' not in data or data['input'] == "":
            self.finish({'success': False, 'message': 'input field required'})
        if 'output' not in data or data['output'] == "":
            self.finish({'success': False, 'message': 'output field required'})

        self.parsed_body = data

    def post(self):
        script_path = self.settings.get('script_path')

        args = [f'python {script_path}']

        flags = self.settings.get('flags')
        if flags is not None and type(flags) == dict:
            for key in flags.keys():
                args.extend([key, flags[key]])

        args.extend(['--input', self.parsed_body['input']])
        args.extend(['--output', self.parsed_body['output']])

        print('args: ', args)   # log args

        ss_res = ' '.join(args)

        out = check_output(ss_res, shell=True)    # TODO: why shell=True
        print("out: ", out)     # parse output?

        # parse results?

        self.finish({'success': True})


# TODO: error handler middleware, logger
def make_app():
    return tornado.web.Application([
        (r"/api/v1/infer", InferHandler),
    ])
