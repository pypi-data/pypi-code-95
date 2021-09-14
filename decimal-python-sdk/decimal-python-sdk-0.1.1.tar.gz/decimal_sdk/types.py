import base64
import json
from hashlib import sha256

from ecdsa import SigningKey, SECP256k1
from ecdsa.util import sigencode_string_canonize

from .wallet import Wallet
from decimal_sdk.msgs.base import BaseMsg
from decimal_sdk.utils import beautify_json
from .tx_types import *

FEES = {
    COIN_SEND: 10,
    COIN_BUY: 10,
    COIN_CREATE: 100,
    COIN_SELL: 100,
    COIN_MULTISEND: 8,
    COIN_SELL_ALL: 100,
    COIN_REDEEM_CHECK: 30,
    VALIDATOR_CANDIDATE: 10000,
    VALIDATOR_DELEGATE: 200,
    VALIDATOR_SET_ONLINE: 100,
    VALIDATOR_SET_OFFLINE: 100,
    VALIDATOR_UNBOND: 200,
    VALIDATOR_CANDIDATE_EDIT: 10000,
    MULTISIG_CREATE_WALLET: 100,
    MULTISIG_CREATE_TX: 100,
    MULTISIG_SIGN_TX: 100,
    PROPOSAL_SUBMIT: 0,
    PROPOSAL_VOTE: 0,
    SWAP_INIT: 33000,
    SWAP_REDEEM: 0,
    COIN_UPDATE: 0,
    NFT_MINT: 0,
    NFT_BURN: 0,
    NFT_EDIT_METADATA: 0,
    NFT_TRANSFER: 0,
    NFT_DELEGATE: 0,
    NFT_UNBOND: 0,
}


class Candidate:
    moniker: str
    identity: str
    website: str
    security_contact: str
    details: str

    def __init__(self, moniker: str, identity: str, website: str, security_contact: str, details: str):
        self.moniker = moniker
        self.identity = identity
        self.website = website
        self.security_contact = security_contact
        self.details = details

    def __dict__(self):
        return {"moniker": self.moniker, "identity": self.identity, "website": self.website,
                "security_contact": self.security_contact, "details": self.details}


class Coin:
    denom: str
    amount: str

    def __init__(self, denom: str, amount: str):
        self.denom = denom
        self.amount = amount

    def __dict__(self):
        return {'denom': self.denom, 'amount': str(self.amount)}


class Signature:
    pub_key: str
    signature: str

    def __init__(self, signature: str, pub_key: str):
        self.pub_key = pub_key
        self.signature = signature

    def __dict__(self):
        return {'pub_key': {'type': 'tendermint/PubKeySecp256k1', 'value': self.pub_key},
                'signature': self.signature}

    def get_signature(self):
        return self.__dict__()


class Fee:
    amount: [Coin]
    gas: str

    def __init__(self, amount: [Coin], gas: str):
        self.amount = amount
        self.gas = gas

    def __dict__(self):
        return {'gas': self.gas, 'amount': [coin.__dict__() for coin in self.amount]}


class SignMeta:
    account_number: str
    chain_id: str
    sequence: str

    def __init__(self, account_number: str = '0', chain_id: str = 'decimal-testnet-12-09-13-00', sequence: str = '1'):
        self.account_number = account_number
        self.chain_id = chain_id
        self.sequence = sequence


class StdSignMsg:
    # Tx part
    fee: Fee
    memo: str
    msgs: [BaseMsg]
    # Meta part
    account_number: str
    chain_id: str
    sequence: str

    signatures: [Signature] = []

    def __init__(self, tx, meta: SignMeta):
        self.fee = tx.fee
        self.msgs = tx.msgs
        self.memo = tx.memo

        self.account_number = meta.account_number
        self.chain_id = meta.chain_id
        self.sequence = meta.sequence

    def add_msg(self, msg: BaseMsg):
        self.msgs.append(msg)

    def sign(self, wallet: Wallet):
        private_key = wallet.get_private_key()
        pub_key = wallet.get_public_key()
        sig = self.__generate_signature(private_key)
        self.signatures = [Signature(signature=sig, pub_key=pub_key)]

    def __get_body_bytes(self):
        data = beautify_json(
            {'fee': self.fee.__dict__(), 'memo': self.memo, 'msgs': [msg.__dict__() for msg in self.msgs],
             'account_number': self.account_number, 'chain_id': self.chain_id, 'sequence': self.sequence})

        return json.dumps(data, separators=(',', ':'), ensure_ascii = False).encode('utf-8')

    def __generate_signature(self, private_key):
        data = self.__get_body_bytes()
        hash_ = sha256(data).digest()
        sk = SigningKey.from_string(private_key, curve=SECP256k1)
        signature = sk.sign_digest_deterministic(hash_, hashfunc=sha256, sigencode=sigencode_string_canonize)
        base_signature = base64.b64encode(signature)

        return base_signature.decode('utf-8')

    def __dict__(self):
        return {'fee': self.fee.__dict__(), 'memo': self.memo, 'msgs': [msg.__dict__() for msg in self.msgs],
                'account_number': self.account_number, 'chain_id': self.chain_id, 'sequence': self.sequence,
                'signatures': [sig.__dict__() for sig in self.signatures]}
