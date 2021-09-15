from scrapyd_api import ScrapydAPI
import requests
from flask import request

from flask import jsonify
import json
from werkzeug.wrappers import Response # resonse to the client
#curl -X POST 'http://localhost:5000/jobs' -H "Content-Type: application/json" -d '{"urls":["www.google.com"], "workers":4}'

def configure_endpoints(app):

    @app.route('/jobs', methods=['POST'])
    def receive_request():
        # I have to run scrapyd before running the function
        # os.system('scrapyd')

        # get request
        data = request.json

        # Connect to the scrapyd API (the server should be already running)
        scrapyd = ScrapydAPI('http://localhost:6800')

        print(scrapyd.list_jobs("scrapymims"))

        # schedule a new job
        settings = {'CONCURRENT_REQUESTS': 1}

        re = scrapyd.schedule('scrapymims', 'images', settings=settings, urls="https://www.bourgeon.co.uk")

        data.update({'jobid': re["jobid"]})

        data = json.dumps(data)

        return data


    @app.route('/jobs/<job_id>/status', methods=['GET'])
    def fetch_status(job_id):

        scrapyd = ScrapydAPI('http://localhost:6800')

        return None

