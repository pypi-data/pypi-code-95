import os
import json
import zipfile
import requests
import time
import csv
from subprocess import check_output
import tornado.ioloop
import tornado.web


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
    uploads_dir = "uploads/"

    # def prepare(self):
    #     data = json_decode(self.request.body)
    #     if 'input' not in data or data['input'] == "":
    #         self.finish({'success': False, 'message': 'input field required'})
    #     if 'output' not in data or data['output'] == "":
    #         self.finish({'success': False, 'message': 'output field required'})
    #     self.parsed_body = data

    def parse_model_result(self, results_path):
        res = dict()
        # INFO: file format: filename, label, confidence, X, Y, W, H
        with open(results_path) as csvfile:
            spamreader = csv.reader(csvfile)
            for row in spamreader:
                print("###", row)
                filename = row[0]

                if filename == 'filename':
                    continue

                if filename not in res:
                    res[filename] = []

                item = {
                    'label': row[1],
                    'confidence': row[2]
                }

                res[filename].append(item)

        return res

    def run_model(self, input_path, output_path):
        script_path = self.settings.get('script_path')
        args = [
            'python', script_path,
            '--input', input_path,
            '--output', output_path
        ]

        flags = self.settings.get('flags')
        if flags is not None and type(flags) == dict:
            for key in flags.keys():
                args.extend([key, flags[key]])

        script_cmd = ' '.join(args)
        print('run script: ', script_cmd)
        out = check_output(script_cmd, shell=True)  # TODO: why shell=True
        print("script out: ", out)

        results_path = os.path.join(output_path, 'result.csv')
        return self.parse_model_result(results_path)

    def async_execution(self, input_path, output_path, url_post_result):
        body = self.run_model(input_path, output_path)
        requests.post(url_post_result, json=body)

    def post(self):
        self.set_header('Content-Type', 'application/json')
        archive = self.request.files.get('archive')

        if archive is None:
            self.set_status(400)
            self.write(json.dumps({'message': 'archive required'}))
            return

        url_post_result = self.get_body_argument('urlPostResult', '')
        async_mode = url_post_result != ''

        archive_filename = archive[0]['filename']

        ts = int(time.time())

        upload_dir_with_ts = os.path.join(self.uploads_dir, str(ts))

        save_path = os.path.join(upload_dir_with_ts, archive_filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        output_file = open(save_path, 'wb')
        output_file.write(archive[0]['body'])

        with zipfile.ZipFile(save_path, 'r') as zip_ref:
            zip_ref.extractall(upload_dir_with_ts)

        print('async_mode: ', async_mode, url_post_result)

        await_dir_with_screenshots = os.path.splitext(save_path)[0]
        print("await_dir_with_screenshots: ", await_dir_with_screenshots)

        if async_mode:
            self.finish({'success': True})
            self.async_execution(
                input_path=await_dir_with_screenshots,
                output_path=upload_dir_with_ts,
                url_post_result=url_post_result)
            return

        body = self.run_model(input_path=await_dir_with_screenshots, output_path=upload_dir_with_ts)
        self.finish(json.dumps(body))


# TODO: error handler middleware, logger
def make_app():
    return tornado.web.Application([
        (r"/api/v1/infer", InferHandler),
    ])
