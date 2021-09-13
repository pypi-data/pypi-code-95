import requests
import json
import math
import time
import pandas as pd

class compliance:
  def __init__(self, upt_standard, upt_domain, upt_customer_id, upt_header, upt_verify):
    self.standard = upt_standard
    self.domain = upt_domain
    self.customer_id = upt_customer_id
    self.header = upt_header
    self.verify = upt_verify
    self.missed_sections = [];
    self.save_path = ".";

  def restcall(self, method, api, post_data=None):
    ### Send the API request

    url=("https://%s.uptycs.io/public/api/customers/%s%s" %
            (self.domain, self.customer_id, api))

    if method == 'GET':
        response = requests.get(url, headers=self.header, verify=self.verify )

    if method == 'POST':
        response = requests.post(url, headers=self.header,
                json=post_data, verify=self.verify )

    if method != 'GET' and method != 'POST':
        return 0

    if (response.status_code != requests.codes.ok):
        error_msg = 'Failed to do request {}. Status code: {}. Response: {}'.format(url, response.status_code, response.content)
        print(error_msg)
        return error_msg
    else:
        return response.json()


  def create_section_query(self, section):
    ### Create the specific query used to pull latest results for each endpoint given a particular standard and section

    return "WITH distinct_results AS (SELECT DISTINCT CONCAT(section, ' ', title) AS section_title, command, compliant, description, evidence, metadata, path, rationale, reason, score, scored, section, version, upt_hostname, upt_asset_id, upt_time, upt_day FROM compliance WHERE standard = '{0}' AND  upt_day >= CAST(date_format(localtimestamp - INTERVAL '1' DAY, '%Y%m%d') AS INTEGER) AND title != '' AND section = '{1}'), latest AS (SELECT *, row_number() OVER (PARTITION BY upt_asset_id, section ORDER BY upt_time DESC) rank_num FROM distinct_results) SELECT * FROM latest WHERE rank_num = 1".format(self.standard, section)


  def get_count(self):
    ### Get a count of total number of rows for a particular standard.  This will be the number of endpoints multiplied by the nubmer of sections for a given standard

    query = "WITH distinct_results AS (SELECT DISTINCT section, upt_asset_id, upt_time, upt_day FROM compliance WHERE standard = '{0}' AND upt_day >= CAST(date_format(localtimestamp - INTERVAL '1' DAY, '%Y%m%d') AS INTEGER) AND title != ''), latest AS (SELECT *, row_number() OVER (PARTITION BY upt_asset_id, section ORDER BY upt_time DESC) rank_num FROM distinct_results) SELECT COUNT(*) AS N FROM latest WHERE rank_num = 1".format(self.standard)

    post_data = {
        'query':query,
        'type':'global',
    }

    response = self.restcall('POST', '/query', post_data)
    count = response.get('items')[0].get('N')
    return count


  def get_sections(self):
    ### Get a list of section numbers for a particular standard

    query = "SELECT section FROM compliance WHERE standard = '" + self.standard + "' AND upt_day >= CAST(date_format(localtimestamp - INTERVAL '1' DAY, '%Y%m%d') AS INTEGER) GROUP BY section"

    post_data = {
        'query':query,
        'type':'global',
    }

    response = self.restcall('POST', '/query', post_data)
    sections = [];
    for i in range(len(response.get('items'))):
        sections.append(response.get('items')[i].get('section'));

    return sections;


  def poll_query_job(self, query_job_id, section):
    ### Poll to see when a particular query job has finished

    api_call = '/queryJobs/%s' % query_job_id
    status = 'QUEUED';
    while (status != 'FINISHED' and status != 'ERROR' and status != 'undefined'):
      response = self.restcall('GET', api_call)
      status = response.get('status')
      #time.sleep(6)

    # If query job does not finish correctly we will save the section number so it can be rerun later
    if status == 'ERROR':
      print('error: ' + response.get('error').get('message').get('detail'));
      self.missed_sections.push(section)
      return 0
    if status == 'undefined':
      print('status undefined')
      self.missed_sections.push(section)
      return 0

    count = response.get('rowCount')
    return count


  def set_save_path(self, path):
    ### Set path to save results

    self.save_path = path


  def save_results(self, query_job_id, section):
    ### Save results from a particular query job

    count = self.poll_query_job(query_job_id, section)

    # We can only collect results in batches of 10,000 so we must loop over count/10,000 to get all results
    for ii in range(math.ceil(count/10000)):
      api_call = '/queryJobs/%s/results?offset=%s' % (query_job_id, ii*10000)
      response = self.restcall('GET', api_call)
      pd.read_json(json.dumps(response.get('items'))).to_csv(self.save_path + "/output_" + section + "_" + str(ii) + ".csv")

    return count


  def get_missed_sections(self):
    ### Get a list of sections that did not finish correctly

    return self.missed_sections


  def run_compliance(self, sections):
    ### Post queries for each section of a particular standard and save results

    print('total number of rows available: ' + str(self.get_count()))
    print ("total number of sections: " + str(len(sections)))

    self.missed_sections = []
    qj_ids = []

    # Post first batch of 20 query jobs
    for i in range(20):
        if i < len(sections):
            post_data = {
                'query': self.create_section_query(sections[i]),
                'type': 'global'
            }

            response = self.restcall('POST', '/queryJobs', post_data)
            qj_ids.append(response.get('id'))

    total = 0

    # Loop over sections to collect query job results and post another batch of query jobs when halfway finished with the previous batch
    for i in range(len(sections)):
        if (i + 10) % 20 == 0 and (i + 10) < len(sections):
            for ii in range(20):
                if (i + 10) + ii < len(sections):
                    post_data = {
                        'query': self.create_section_query(sections[(i + 10) + ii]),
                        'type': 'global'
                    }

                    response = self.restcall('POST', '/queryJobs', post_data)
                    qj_ids.append(response.get('id'))

        count = self.save_results(qj_ids[i], sections[i])
        total += count



    print("total number of rows retrieved: " + str(total) + " rows")
    return 0
