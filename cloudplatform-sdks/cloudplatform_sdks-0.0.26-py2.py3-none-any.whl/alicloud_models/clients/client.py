from aliyunsdkcore.client import AcsClient
import json

class AliCloudClient:
    def __init__(self, secret_id, secret_key, region, config, product_code=None):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.config = config
        self.product_code = product_code
        self.client = self._client()

    def _client(self):
        client = AcsClient(self.secret_id, self.secret_key, self.region)
        cloud_type = self.config.get('cloud_type', '')
        if cloud_type == 'aliapsara':
            product_domain_type = self.product_code + '_endpoint'
            endpoint = self.config.get(product_domain_type)
            client.add_endpoint(region_id=self.region,
                                product_code=self.product_code,
                                endpoint=endpoint)
        return client

    def do_request(self, req_cls, query_params=None, body_params=None):
        req = req_cls()
        if query_params:
            for k, v in query_params.items():
                req.add_query_param(k, v)
        if body_params:
            for k, v in body_params.items():
                req.add_body_params(k, v)
        try:
            res = self.client.do_action_with_exception(req)
        except Exception as e:
            raise e
        return json.loads(res)
