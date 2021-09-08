from django.test import TestCase


class TestSetUp(TestCase):
    """Class with setup and teardown for tests in XIS"""

    def setUp(self):
        """Function to set up necessary data for testing"""

        # globally accessible data sets

        self.supplemental_api_endpoint = 'http://openlxp-xis:8020' \
                                         '/api/supplemental-data/'

        self.receive_email_list = ['receiver1@openlxp.com',
                                   'receiver1@openlxp.com']
        self.sender_email = "sender@openlxp.com"

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
