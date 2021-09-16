import requests
from datetime import datetime, timedelta

class TAPClient(object):
    def __init__(self, sp, key, base_url=None):
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = 'https://tap-api-v2.proofpoint.com/v2'
        self.sp = sp
        self.key = key

    def get_all_events(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/all'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)
        
    def get_clicks_permitted(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/clicks/permitted'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)

    def get_clicks_blocked(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/clicks/blocked'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)

    def get_messages_delivered(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/messages/delivered'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)

    def get_messages_blocked(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/messages/blocked'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)

    def get_issues(self, params=None, sinceSeconds=None, format=None):
        endpoint = '/siem/issues'
        params = self._validate_siem_params(params, sinceSeconds, format)
        return self._get_response(endpoint, params=params)

    def get_forensics(self, threatID=None, campaignID=None, includeCampaignForensics=False):
        endpoint = '/forensics'
        params = {
            'includeCampaignForensics': includeCampaignForensics
        }

        if threatID:
            params['threatId'] = threatID
        elif campaignID:
            params['campaignId'] = campaignID
        else:
            print('threatID or campaignID required for get_forensics')
            return
            
        return self._get_response(endpoint, params=params)

    def get_campaign(self, campaignID):
        endpoint = f'/campaign/{campaignID}'
        return self._get_response(endpoint, params=None)

    def get_all_campaigns(self, params=None, interval=None, details=False):
        endpoint = '/campaign/ids'
        params = self._validate_campaign_params(params, interval)
        return self._get_response(endpoint, params=params)
    
    def get_threat_details(self, threatID):
        endpoint = f'/threat/summary/{threatID}'
        return self._get_response(endpoint)

    def get_vap_report(self, params=None, window=None):
        endpoint = '/people/vap'
        params = self._validate_people_params(params, window)
        return self._get_response(endpoint, params=params)

    def get_top_clicker_report(self, params=None, window=None):
        endpoint = '/people/top-clickers'
        params = self._validate_people_params(params, window)
        return self._get_response(endpoint, params=params)

    def decode_url(self, data):
        endpoint = '/url/decode'
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(self.base_url + endpoint, headers=headers, json=data, auth=(self.sp, self.key))
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Error encountered during API Call: {resp.text}")
            exit(1)

    def _get_response(self, endpoint, params=None):
        resp = requests.get(self.base_url + endpoint, params=params, auth=(self.sp, self.key))
        if resp.status_code in [200, 204]:
            return resp.text
        else:
            print(f"Error encountered during API Call: {resp.text}")
            exit(1)

    def _validate_siem_params(self, params, sinceSeconds, format):
        if not params:
            params = {}
            if not sinceSeconds:
                params['sinceSeconds'] = 600
            else:
                params['sinceSeconds'] = sinceSeconds

            if not format:
                params['format'] = 'json'
            else:
                params['format'] = format
            return params
        else:
            for param in params:
                if param not in ['interval', 'sinceSeconds', 'sinceTime', 'format', 'threatStatus', 'threatType']:
                    del params[param]

            if 'interval' not in params and 'sinceSeconds' not in params and 'sinceTime' not in params:
                params['sinceSeconds'] = 600
            if 'format' not in params:
                params['format']  = 'json'
            return params

    def _get_default_campaign_interval(self):
        # default interval is now - 1 day
        now = datetime.now()
        now = now.replace(second=0, microsecond=0)
        delta = timedelta(days=1)
        start = now - delta
        return f'{start.isoformat()}Z/{now.isoformat()}Z'

    def _validate_campaign_params(self, params, interval):
        if not params:
            params = {}
            if not interval:
                params['interval'] = self._get_default_campaign_interval()
            else:
                params['interval'] = interval
            return params
        else:
            for param in params:
                if param not in ['interval', 'size', 'page']:
                    del params[param]
            
            if 'interval' not in params:
                params['interval'] = self._get_default_campaign_interval()
            return params

    def _validate_people_params(self, params, window):
        if not params:
            params = {}
            if not window:
                params['window'] = 30
            else:
                params['window'] = window
            return params
        else:
            for param in params:
                if param not in ['window', 'size', 'page']:
                    del params[param]
            
            if 'window' not in params:
                params['window'] = 30
            return params