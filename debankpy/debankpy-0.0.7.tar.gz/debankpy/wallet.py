import logging

_LOGGER = logging.getLogger(__name__)

class Wallet:
    def __init__(self, address):
        self._address = address
        self._balance = 0.0
        self._tokenList = {}
        return

    def setAddress(self, address):
        self._address = address

    def getAddress(self):
        return self._address

    def getBalance(self):
        return self._balance

    def setBalance(self, balance):
        logging.debug("Balance: %s", balance)
        self._balance = balance

    def updateBalance(self, appendBalance):
        logging.debug("Update Balance: %s", appendBalance)
        self._balance = self._balance + appendBalance

    def getTokenList(self):
        return self._tokenList

    def setTokenList(self, tokenId, tokenName, tokenValue):
        self._tokenList.update({tokenId: [tokenName, tokenValue]})