from ad_api.base import Client, sp_endpoint, fill_query_params, ApiResponse

class ProductTargeting(Client):

    @sp_endpoint('/v2/sp/targets', method='GET')
    def list_products_targeting_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), params=kwargs)

    @sp_endpoint('/v2/sp/targets/extended', method='GET')
    def list_products_targeting_extended_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), params=kwargs)

    @sp_endpoint('/v2/sp/targets/{}', method='GET')
    def get_products_targeting_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)

    @sp_endpoint('/v2/sp/targets/extended/{}', method='GET')
    def get_products_targeting_extended_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)

    @sp_endpoint('/v2/sp/targets/brands', method='GET')
    def get_brand_targeting_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), params=kwargs)

    @sp_endpoint('/v2/sp/targets', method='PUT')
    def edit_products_targeting_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), data=kwargs.pop('body'), params=kwargs)

    @sp_endpoint('/v2/sp/targets', method='POST')
    def create_products_targeting_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), data=kwargs.pop('body'), params=kwargs)

    @sp_endpoint('/v2/sp/targets/productRecommendations', method='POST')
    def get_products_targeting_recommendations_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), data=kwargs.pop('body'), params=kwargs)

    @sp_endpoint('/v2/sp/targets/{}', method='DELETE')
    def delete_products_targeting_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)