import json
import requests
import time
import logging
import datakitchen_api_tools.dk_api_helpers as dk_api_helpers
from datakitchen_api_tools.DKOrder import DKOrder
from datakitchen_api_tools.DKExceptions import *

logger = logging.getLogger("datakitchen_api_tools.DkConnection")

class DKConnection():
    def __init__(self, hostname, username, password, timeout=1):
        self.hostname = hostname
        payload = {'username': username, 'password': password}
        r = requests.post('https://%s/v2/login' % hostname, data=payload)
        if r.text == 'Credentials are invalid':
            raise Exception
        if "\n" in r.text or "\r" in r.text:
            logger.error("Error: Platform returned invalid token." % (kitchen, recipe, variation))
        self.token = r.text
        self.headers =  {'content-type': 'application/json', 'authorization': 'bearer ' + self.token}

    def createOrder(self, kitchen, recipe, variation, overrides={}, retries=0):
        headers = {'content-type': 'application/json', 'authorization': 'bearer ' + self.token}
        url = 'https://%s/v2/order/create/%s/%s/%s' % (self.hostname, kitchen, recipe, variation)
        payload = {'parameters': overrides, "schedule" : "now"}
        response = requests.put(url, headers=headers, data=json.dumps(payload))
        attempts = 0
        while attempts < retries and response.status_code != 200:
            response = requests.put(url, headers=headers, data=json.dumps(payload))
            time.sleep(60)
            attempts += 1
        return response

    def safeCreateOrder(self, kitchen, recipe, variation, overrides={}, wait_time=10, timeout=50000, test_level=""):
        response = self.createOrder(kitchen, recipe, variation, overrides=overrides)
        if response.status_code != 200:
            logger.error("Error Starting Order %s %s %s." % (kitchen, recipe, variation))
            raise DKOrderStartException
        order = json.loads(response.text)
        order_id = order['order_id']
        logger.info(order_id)
        order_run = self.getOrder(kitchen, order_id)
        time.sleep(wait_time)
        time_running = 0
        while order_run.isOrderRunning() and time_running < timeout:
            time.sleep(wait_time)
            order_run = self.getOrder(kitchen, order_id)
            time_running += wait_time
        if time_running >= timeout:
            raise DKTimeoutException
        if not order_run.didOrderCompleteSuccesfully():
            logger.error("Order %s, %s, %s Failed." % (kitchen, recipe, variation))
            raise DKOrderRunErrorException
        if len(order_run.getFailedTests(test_level)) > 0:
            logger.error("Tests in Order  %s, %s, %s Failed." % (kitchen, recipe, variation))
            raise DKOrderRunFailedTestException
        return order_run

    def OrderInfo(self, kitchen, order_id):
        url = "https://%s/v2/order/details/%s" % ( self.hostname, kitchen)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = {'order_id': order_id, 'summary': True, 'logs': True, 'timingresults': True,
                   'testresults': True, 'servingjson': True, "schedule": "now"}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if "does not exist." in r.text:
            raise Exception("Order run id %s not found." % order_run_id )
        return DKOrder(json.loads(r.text))

    def OrderRunInfo(self, kitchen, order_run_id):
        url = "https://%s/v2/order/details/%s" % (self.hostname, kitchen)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}
        payload = {'serving_hid': order_run_id, 'testresults': True}
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        if "does not exist." in r.text:
            raise Exception("Order run id %s not found." % order_run_id)
        return DKOrder(json.loads(r.text))

    def getOrder(self, kitchen, order_id):
        return self.OrderInfo(kitchen, order_id)

    def TestsFromOrderRun(self, kitchen, order_run_id):
        return self.getOrderRun(kitchen, order_run_id).getTests()

    def OrderStatus(self, kitchen, order_run):
        return self.getOrder(kitchen, order_run_id).getOrderStatus()
