from ad_api.base import Client, sp_endpoint, fill_query_params, ApiResponse

class NegativeTargets(Client):

    @sp_endpoint('/v2/sp/negativeTargets', method='POST')
    def create_negative_targets_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), data=kwargs.pop('body'), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets', method='PUT')
    def edit_negative_targets_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), data=kwargs.pop('body'), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets', method='GET')
    def list_negative_targets_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets/{}', method='GET')
    def get_negative_targets_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets/{}', method='DELETE')
    def delete_negative_targets_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets/extended', method='GET')
    def list_negative_targets_extended_request(self, **kwargs) -> ApiResponse:
        return self._request(kwargs.pop('path'), params=kwargs)

    @sp_endpoint('/v2/sp/negativeTargets/extended/{}', method='GET')
    def get_negative_targets_extended_request(self, targetId, **kwargs) -> ApiResponse:
        return self._request(fill_query_params(kwargs.pop('path'), targetId), params=kwargs)