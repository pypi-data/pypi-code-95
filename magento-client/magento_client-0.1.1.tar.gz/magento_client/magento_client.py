#!/usr/bin/env python3
from __future__ import unicode_literals

from magento_client.rest_client import RestAPIClient


class Magento(RestAPIClient):


    def __init__(self,
                 url,
                 consumer_key,
                 consumer_secret,
                 access_token,
                 access_token_secret,
                 advanced_mode=False,
                 ):
        super().__init__(
            url,
            consumer_key,
            consumer_secret,
            access_token,
            access_token_secret,
            advanced_mode,
        )

    def get(self, path, data=None, flags=None, params=None, headers=None, not_json_response=None, trailing=None):
        resp = super().get(path=path, data=data, flags=flags, params=params, headers=headers,
                           not_json_response=not_json_response, trailing=trailing)

        # single item returned
        if 'results' not in resp:
            return resp

        # multiple items
        results = resp['results']

        # handle all results paginated
        while 'next' in resp.get('metadata'):
            resp = super().get(resp.get('metadata').get('next'))
            results.extend(resp['results'])

        return results

    def set_category_position(self, product_sku, category_id, position):

        """
        Ser position for a product in a given category.
        """
        data = {
            "productLink": {
                "sku": product_sku,
                "position": position,
                "category_id": category_id,
            }
        }

        path = f"/categories/{category_id}/products"

        return self.put(path=path, data=data)


    def get_categories(self):

        """
        Get magento categories.
        """


        path = f"/categories"

        return self.get(path=path)
