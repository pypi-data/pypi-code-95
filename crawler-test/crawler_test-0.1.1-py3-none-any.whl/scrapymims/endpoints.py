import re
import uuid
import os
import requests
from flask import request
from flask import render_template
from flask import jsonify
from flask import url_for
from flask import abort


import json
from werkzeug.exceptions import BadRequest

def configure_endpoints(app):

    @app.route('/jobs', methods=['POST'])
    def receive_request():
        """
        curl -X POST -H "Content-Type: application/json" -d '{ "workers": 4, "urls":["https://www.google.com/"]}' http://localhost:5000/jobs
        :return:
        """
        data = request.get_json()

        # Launch scrapyd
        os.system('scrapyd')

        # Launch job as a spider

        os.system('curl http://localhost:6800/schedule.json -d project=scrapymims -d spider=images')
        # need to merge the two projects toghether to be able ti run the images spider



        #url = "http://localhost:6800/schedule.json" # this should go into settings

        #headers = {"content-type": "application/json", "Accept-Charset": "UTF-8"} # this should go into settings

        #r = requests.post(url, data={"sample": "data"})

        #data = r.json()

        # From scrapyd get the running in progress of the job_id
        #os.system('curl http://localhost:6800/schedule.json -d project=scrapysrc -d spider=images')

        return data

