import requests
import json
import time
import enum


class CalculationType(enum.Enum):
    AMORTIZING_SWAP = "amortizing-swap"
    ASIAN_OPTION = "asian-option"
    BASIS_SWAP = "basis-swap"
    CAP_VOLATILITY = "cap-volatility"
    CC_SWAP = "cc-swap"
    DEPOSIT = "deposit"
    EWMA = "ewma"
    FIXED_RATE_BOND = "fixed-rate-bond"
    FLOATING_BOND = "floating-bond"
    FORWARD_RATE_AGREEMENT = "forward-rate-agreement"
    FX_FORWARD = "fx-forward"
    FX_SWAP = "fx-swap"
    INFLATION_CPI_BOND = "inflation-cpi-bond"
    INTEREST_RATES_SWAP = "interest-rates-swap"
    LOAN = "loan"
    ND_FORWARD = "nd-forward"
    OVERNIGHT_INDEX_SWAP = "overnight-index-swap"
    RISK = "risk"
    SWAPTION = "swaption"
    VANILLA_OPTION = "vanilla-option"
    VANNA_VOLGA = "vanna-volga"
    VOLATILITY_SURFACE = "vol-surface"
    YIELD_CURVE_CALCULATION = "yield-curve-calculation"
    ZERO_COUPON_BOND = "zero-coupon-bond"


class RhoovaError(Exception):
    def __init__(self, message):
        self.message = message

    def printPretty(self):
        try:
            print(json.dumps(json.loads(self.message), indent=4))
        except json.decoder.JSONDecodeError:
            print(self.message)


class ClientConfig:
    def __init__(self, apiKey: str, apiSecret: str):
        self.apiUrl = "https://app.rhoova.com/api"
        self.apiKey = apiKey
        self.apiSecret = apiSecret


class Api:
    def __init__(self, config: ClientConfig):
        self.config = config

    def createTask(self, calculationType: CalculationType, data):
        if not isinstance(calculationType, CalculationType):
            raise TypeError('Calculation must be an instance of CalculationType')
        url = self.config.apiUrl + "/tasks/" + calculationType.value + "?apiClient=true"
        response = requests.post(url=url, data=json.dumps(data), headers={
            'Content-type': 'application/json',
            'ekx-api-key': self.config.apiKey,
            'ekx-api-secret': self.config.apiSecret
        })
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise RhoovaError(response.text)

    def getTaskResult(self, taskID):
        url = self.config.apiUrl + "/tasks/" + taskID
        response = requests.get(url=url, headers={
            'Content-type': 'application/json',
            'ekx-api-key': self.config.apiKey,
            'ekx-api-secret': self.config.apiSecret
        })
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['error'] is not None:
                raise RhoovaError(data['error'])
            else:
                return data
        else:
            raise RhoovaError(response.text)

    def createTaskAndWaitForResult(self, calculationType: CalculationType, data, maxTryCount=6, tryInterval=5):
        task = self.createTask(calculationType, data)
        while maxTryCount > 0:
            data = self.getTaskResult(task["taskID"])
            if data["result"] is not None:
                return data
            else:
                maxTryCount = maxTryCount - 1
                time.sleep(tryInterval)
        raise RhoovaError("Task created but result timed out. TaskID : " + task["taskID"])
