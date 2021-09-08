import requests
from requests.adapters import HTTPAdapter
from . import counter, validation, utils

c = counter.Counter(0)
req_session = requests.Session()

# do we ever want to retry here and cause side effects? or we should fail and log
req_session.mount('http://', HTTPAdapter(max_retries=0))
req_session.mount('https://', HTTPAdapter(max_retries=0))

class VeriteosClient():
    def __init__(self, options:dict) -> None:
        veriteos_client = validation.VeriteosClientSchema()
        veriteos_client.load(options)
        self.version = '0.0.1-py'
        self.sentinel_uri = options['sentinel_uri']
        self.should_send_data = options['should_send_data']

    def register(self, event: validation.ClientEventSchema):
        """
        Args:
                event : {
                pipeline: {
                        name : str
                        version : str
                        user : str
                },
                event_meta_data: {
                        task_name : str
                        task_version : str
                        task_environment : str
                },
                event_data: {
                        payload : Dict
                        type : str
                        uri : str
                        source : str
                        destination : str
                },
                event_reporter: {
                        name :str
                }
                }
        """
        event_schema = validation.ClientEventSchema()
        valid_data = event_schema.load(event)
        enriched_data = utils.enrich_valid_event(valid_data, self.version, c.get_count())

        try:    
                if not self.should_send_data:
                        del enriched_data['data']['payload']

                event_url = '/reporter_events/'
                res = req_session.post(url=self.sentinel_uri + event_url, json=enriched_data, timeout=1)

                if  '50' in str(res.status_code):
                        print( '\033[93m' +  'Event could not be forwarded to veriteos sentinel, it is unreachable with a status code of:', res.status_code, '\033[0m')        

        except Exception as ex:
                print( '\033[93m' +  'Event could not be forwarded to veriteos sentinel: ', ex, '\033[0m')
                
