from directory_api_client.base import AbstractAPIClient

url_unsubscribe = '/notifications/anonymous-unsubscribe/'


class NotificationsAPIClient(AbstractAPIClient):
    def anonymous_unsubscribe(self, signed_email_address):
        return self.post(url=url_unsubscribe, data={'email': signed_email_address})
