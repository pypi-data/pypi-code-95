import json
import csv
import requests
import re
from http.client import responses
from jsonpath_ng import jsonpath, parse as jparse

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException


class NovigiJsonToCSVExportOperator(BaseOperator):

    template_fields = ['api_headers']


    def __init__(self, api_url: str, req_type = "GET", output_csv = "", json_path: str = None, api_headers: dict = None, pay_load: dict = None, mapping: dict = {}, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.api_url = api_url
            self.req_type = req_type
            self.output_csv = output_csv
            self.json_path = json_path
            self.api_headers = api_headers
            self.pload = pay_load
            self.mapping = mapping


    def execute(self, context):

            response = requests.request(self.req_type, self.api_url ,headers = self.api_headers,data = self.pload)

            sucess_range = re.search(r'2[0-9][0-9]', str(response.status_code))

            if not (sucess_range):
                raise AirflowException("Response status code is " + str(response.status_code) + " and response status is '"+ responses[response.status_code]+"'")

            data = response.json()

            jsonpath_expression = jparse(self.json_path)

            match = jsonpath_expression.find(data)

            if len(match) > 0:

                result = match[0].value

            else:
                raise AirflowException('can not get match')

            # now we will open a file for writing
            data_file = open(self.output_csv,'w')

            # create the csv writer object
            csv_writer = csv.writer(data_file)

            # Writing headers of CSV file
            header = self.mapping.keys()

            csv_writer.writerow(header)

            for values_in_result in result:

                row = []

                for each_value in self.mapping.values():

                    jsonpath_exp = jparse(each_value)

                    matcher = jsonpath_exp.find(values_in_result)

                    mapping_value = ''

                    if len(matcher) > 0:
                        mapping_value = matcher[0].value

                    row.append(mapping_value)

                csv_writer.writerow(row)

            data_file.close()

            return True
