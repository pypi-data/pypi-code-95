import time
from decimal_sdk.msgs.base import BaseMsg
from decimal_sdk.tx_types import *
from decimal_sdk.types import Coin, Candidate, Signature
from ..utils.helpers import get_amount_uni


class SendCoinMsg(BaseMsg):
    type = COIN_SEND
    sender: str
    receiver: str
    coin: Coin

    def __init__(self, sender: str, receiver: str, coin: Coin):
        self.sender = sender
        self.receiver = receiver
        self.coin = coin

    def __dict__(self):
        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'receiver': self.receiver,
                'coin': self.coin.__dict__()
            }
        }


class BuyCoinMsg(BaseMsg):
    type = COIN_BUY
    sender: str
    coin_to_buy: Coin
    max_coin_to_sell: Coin

    def __init__(self, sender: str, coin_to_buy: Coin, max_coin_to_sell: Coin):
        self.sender = sender
        self.coin_to_buy = coin_to_buy
        self.max_coin_to_sell = max_coin_to_sell

    def __dict__(self):
        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'coin_to_buy': self.coin_to_buy.__dict__(),
                'max_coin_to_sell': self.max_coin_to_sell.__dict__()
            }
        }


class SellCoinMsg(BaseMsg):
    type = COIN_SELL
    sender: str
    coin_to_sell: Coin
    min_coin_to_buy: Coin

    def __init__(self, sender: str, coin_to_sell: Coin, min_coin_to_buy: Coin):
        self.sender = sender
        self.coin_to_sell = coin_to_sell
        self.min_coin_to_buy = min_coin_to_buy

    def __dict__(self):
        return {'type': self.type,
                'value': {
                    'sender': self.sender,
                    'coin_to_sell': self.coin_to_sell.__dict__(),
                    'min_coin_to_buy': self.min_coin_to_buy.__dict__()
                }}


class CreateCoinMsg(BaseMsg):
    type = COIN_CREATE
    sender: str
    title: str
    symbol: str
    crr: int
    initial_volume: str
    initial_reserve: str
    identity: str
    limit_volume: str

    def __init__(self,
                 sender: str,
                 title: str,
                 symbol: str,
                 crr: int,
                 initial_volume: str,
                 initial_reserve: str,
                 identity: str,
                 limit_volume: str):
        self.sender = sender
        self.title = title
        self.symbol = symbol
        self.crr = crr
        self.initial_volume = initial_volume
        self.initial_reserve = initial_reserve
        self.identity = identity
        self.limit_volume = limit_volume

    def __dict__(self):
        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'title': self.title,
                'symbol': self.symbol,
                'constant_reserve_ratio': self.crr,
                'initial_volume': self.initial_volume,
                'initial_reserve': self.initial_reserve,
                'identity': self.identity,
                'limit_volume': self.limit_volume
                }
            }


class UpdateCoinMsg(BaseMsg):
    type = COIN_UPDATE
    sender: str
    symbol: str
    identity: str
    limit_volume: str

    def __init__(self,
                 sender: str,
                 symbol: str,
                 identity: str,
                 limit_volume: str):
        self.sender = sender
        self.symbol = symbol
        self.identity = identity
        self.limit_volume = limit_volume

    def __dict__(self):
        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'symbol': self.symbol,
                'identity': self.identity,
                'limit_volume': self.limit_volume
                }
            }


class SellAllCoinsMsg(BaseMsg):
    type = COIN_SELL_ALL
    sender: str
    coin_to_sell: Coin
    min_coin_to_buy: Coin

    def __init__(self, sender: str, coin_to_sell: Coin, min_coin_to_buy: Coin):
        self.sender = sender
        self.coin_to_sell = coin_to_sell
        self.min_coin_to_buy = min_coin_to_buy

    def __dict__(self):
        return {'type': self.type,
                'value': {
                    'sender': self.sender,
                    'coin_to_sell': self.coin_to_sell.__dict__(),
                    'min_coin_to_buy': self.min_coin_to_buy.__dict__()
                }}


class DelegateMsg(BaseMsg):
    type = VALIDATOR_DELEGATE
    delegator_address: str
    validator_address: str
    coin: Coin

    def __init__(self, delegator_address: str, validator_address: str, coin: Coin):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.coin = coin

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "delegator_address": self.delegator_address,
                "validator_address": self.validator_address,
                "coin": self.coin.__dict__()
            }
        }


class UnboundMsg(BaseMsg):
    type = VALIDATOR_UNBOND
    delegator_address: str
    validator_address: str
    coin: Coin

    def __init__(self, delegator_address: str, validator_address: str, coin: Coin):
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.coin = coin

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "delegator_address": self.delegator_address,
                "validator_address": self.validator_address,
                "coin": self.coin.__dict__()
            }
        }


class DeclareCandidateMsg(BaseMsg):
    type = VALIDATOR_CANDIDATE
    commission: int
    validator_addr: str
    reward_addr: str
    pub_key: Signature
    stake: Coin
    description: Candidate

    def __init__(self, commission: int, validator_addr: str, reward_addr: str, pub_key: Signature,
                 stake: Coin, description: Candidate):
        self.commission = commission
        self.validator_addr = validator_addr
        self.reward_addr = reward_addr
        self.pub_key = pub_key
        self.stake = stake
        self.description = description

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "commission": str(self.commission),
                "validator_addr": self.validator_addr,
                "reward_addr": self.reward_addr,
                "pub_key": self.pub_key,
                "stake": self.stake.__dict__(),
                "description": self.description.__dict__()
            }
        }


class EditCandidateMsg(BaseMsg):
    type = VALIDATOR_CANDIDATE_EDIT
    validator_address: str
    reward_address: str
    description: Candidate

    def __init__(self, validator_address: str, reward_address: str, description: Candidate):
        self.validator_address = validator_address
        self.reward_address = reward_address
        self.description = description

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "validator_address": self.validator_address,
                "reward_address": self.reward_address,
                "description": self.description.__dict__()
            }
        }


class DisableEnableValidatorMsg(BaseMsg):
    type: str
    validator_address: str

    state = {
        "disable": VALIDATOR_SET_OFFLINE,
        "enable": VALIDATOR_SET_ONLINE
    }

    def __init__(self, set_state: str, validator_address: str):
        self.type = self.state[set_state]
        self.validator_address = validator_address

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "validator_address": self.validator_address
            }
        }


class MultysigCreateMsg(BaseMsg):
    type = MULTISIG_CREATE_WALLET
    sender: str
    owners: list
    weights: list
    threshold: int

    def __init__(self, sender: str, owners: list, weights: list, threshold: int):
        self.sender = sender
        self.owners = owners
        self.weights = weights
        self.threshold = threshold

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "sender": self.sender,
                "owners": self.owners,
                "weights": self.weights,
                "threshold": self.threshold
            }
        }


class MultysigCreateTXMsg(BaseMsg):
    type = MULTISIG_CREATE_TX
    sender: str
    wallet: str
    receiver: str
    coins: Coin

    def __init__(self, sender: str, wallet: str, receiver: str, coins: Coin):
        self.sender = sender
        self.wallet = wallet
        self.receiver = receiver
        self.coins = coins

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "sender": self.sender,
                "wallet": self.wallet,
                "receiver": self.receiver,
                "coins": self.coins.__dict__()
            }
        }


class MultysigSignTXMsg(BaseMsg):
    type = MULTISIG_SIGN_TX

    sender: str
    tx_id: str

    def __init__(self, sender: str, tx_id: str):
        self.sender = sender
        self.tx_id = tx_id

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "sender": self.sender,
                "tx_id": self.tx_id
            }
        }


class MultisendSend:
    receiver: str
    coin: Coin

    def __init__(self, receiver: str, coin: Coin):
        self.receiver = receiver
        self.coin = coin

    def __dict__(self):
        return {
            "coin": self.coin.__dict__(),
            "receiver": self.receiver
        }


class MultisendCoinMsg(BaseMsg):
    type = COIN_MULTISEND

    sender: str
    sends: [MultisendSend]

    def __init__(self, sender: str, sends: [MultisendSend]):
        self.sender = sender
        self.sends = sends

    def __dict__(self):
        snds = []
        for send in self.sends:
            snds.append({
                "receiver": send["receiver"],
                "coin": {
                    "amount": get_amount_uni(send["amount"]),
                    "denom": send["coin"]
                }
            })

        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'sends': snds
            }
        }


class SubmitProposalMsg(BaseMsg):
    type = PROPOSAL_SUBMIT
    content: str
    proposer: str
    voting_start_block: str
    voting_end_block: str

    def __init__(self, content: str, proposer: str, voting_start_block: str, voting_end_block: str):
        self.content = content
        self.proposer = proposer
        self.voting_start_block = voting_start_block
        self.voting_end_block = voting_end_block

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "content": self.content,
                "proposer": self.proposer,
                "voting_start_block": self.voting_start_block,
                "voting_end_block": self.voting_end_block,
            }
        }


class VoteProposalMsg(BaseMsg):
    type = PROPOSAL_VOTE
    proposal_id: int
    voter: str
    option: str

    def __init__(self, proposal_id: int, voter: str, option: str):
        self.proposal_id = proposal_id
        self.voter = voter
        self.option = option

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "proposal_id": self.proposal_id,
                "voter": self.voter,
                "option": self.option
            }
        }


class RedeemCheckMsg(BaseMsg):
    type = COIN_REDEEM_CHECK
    sender: str
    check: str
    proof: str

    def __init__(self, sender: str, check: str, proof: Coin):
        self.sender = sender
        self.check = check
        self.proof = proof

    def __dict__(self):
        return {
            'type': self.type,
            'value': {
                'sender': self.sender,
                'check': self.check,
                'proof': self.proof
            }
        }


class SwapRedeemMsg(BaseMsg):
    type = SWAP_REDEEM
    sender: str
    sent_from: str
    recipient: str
    amount: str
    token_name: str
    token_symbol: str
    from_chain: str
    dest_chain: str
    v: str
    r: str
    s: str

    def __init__(self, sender: str,
                 sent_from: str,
                 recipient: str,
                 amount: str,
                 token_name: str,
                 token_symbol: str,
                 from_chain: str,
                 dest_chain: str,
                 v: str, r: str, s: str):
        self.sender = sender
        self.sent_from = sent_from
        self.recipient = recipient
        self.amount = amount
        self.token_name = token_name
        self.token_symbol = token_symbol
        self.from_chain = from_chain
        self.dest_chain = dest_chain
        self.v = v
        self.r = r
        self.s = s

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                'sender': self.sender,
                'from': self.sender,
                'recipient': self.recipient,
                'amount': self.amount,
                'token_name': self.token_name,
                'token_symbol': self.token_symbol,
                'transaction_number': str(round(time.time() * 1000)),
                'from_chain': self.from_chain,
                'dest_chain': self.dest_chain,
                'v': self.v,
                'r': self.r,
                's': self.s,
            }
        }


class SwapInitMsg(BaseMsg):
    type = SWAP_INIT
    sender: str
    recipient: str
    amount: str
    token_symbol: str
    from_chain: str
    dest_chain: str

    def __init__(self, sender: str, recipient: str, amount: str, token_symbol: str, from_chain: str, dest_chain: str):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.token_symbol = token_symbol
        self.from_chain = from_chain
        self.dest_chain = dest_chain

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                'from': self.sender,
                'recipient': self.recipient,
                'amount': self.amount,
                'token_symbol': self.token_symbol,
                'transaction_number': str(round(time.time() * 1000)),
                'from_chain': self.dest_chain,
                'dest_chain': self.dest_chain,
            }
        }


class NftMintMsg(BaseMsg):
    type = NFT_MINT
    denom: str
    id: str
    sender: str
    recipient: str
    quantity: str
    reserve: str
    token_uri: str
    allow_mint: bool

    def __init__(self, denom: str, id: str, sender: str, recipient: str, quantity: int, reserve: int, token_uri: str,
                 allow_mint: bool):
        if not isinstance(quantity, int):
            raise ValueError('Quantity must be of type int')
        self.denom = denom
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.quantity = str(quantity)
        self.reserve = str(get_amount_uni(reserve))
        self.token_uri = token_uri
        self.allow_mint = allow_mint

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "sender": self.sender,
                "recipient": self.recipient,
                "quantity": self.quantity,
                "reserve": self.reserve,
                "token_uri": self.token_uri,
                "allow_mint": self.allow_mint,
            }
        }


class NftBurnMsg(BaseMsg):
    type = NFT_BURN
    denom: str
    id: str
    sender: str
    sub_token_ids: []

    def __init__(self, denom: str, id: str, sender: str, sub_token_ids: []):
        self.denom = denom
        self.id = id
        self.sender = sender
        self.sub_token_ids = sub_token_ids

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "sender": self.sender,
                "sub_token_ids": self.sub_token_ids,
            }
        }


class NftEditMetadataMsg(BaseMsg):
    type = NFT_EDIT_METADATA
    denom: str
    id: str
    sender: str
    token_uri: str

    def __init__(self, denom: str, id: str, sender: str, token_uri: str):
        self.denom = denom
        self.id = id
        self.sender = sender
        self.token_uri = token_uri

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "sender": self.sender,
                "token_uri": self.token_uri,
            }
        }


class NftTransferMsg(BaseMsg):
    type = NFT_TRANSFER
    denom: str
    id: str
    sender: str
    recipient: str
    sub_token_ids: []

    def __init__(self, denom: str, id: str, sender: str, recipient: str, sub_token_ids: []):
        self.denom = denom
        self.id = id
        self.sender = sender
        self.recipient = recipient
        self.sub_token_ids = sub_token_ids

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "sender": self.sender,
                "recipient": self.recipient,
                "sub_token_ids": self.sub_token_ids,
            }
        }


class NftDelegateMsg(BaseMsg):
    type = NFT_DELEGATE
    denom: str
    id: str
    delegator_address: str
    validator_address: str
    sub_token_ids: []

    def __init__(self, denom: str, id: str, delegator_address: str, validator_address: str, sub_token_ids: []):
        self.denom = denom
        self.id = id
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.sub_token_ids = sub_token_ids

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "delegator_address": self.delegator_address,
                "validator_address": self.validator_address,
                "sub_token_ids": self.sub_token_ids,
            }
        }


class NftUnboundMsg(BaseMsg):
    type = NFT_UNBOND
    denom: str
    id: str
    delegator_address: str
    validator_address: str
    sub_token_ids: []

    def __init__(self, denom: str, id: str, delegator_address: str, validator_address: str, sub_token_ids: []):
        self.denom = denom
        self.id = id
        self.delegator_address = delegator_address
        self.validator_address = validator_address
        self.sub_token_ids = sub_token_ids

    def __dict__(self):
        return {
            "type": self.type,
            "value": {
                "denom": self.denom,
                "id": self.id,
                "delegator_address": self.delegator_address,
                "validator_address": self.validator_address,
                "sub_token_ids": self.sub_token_ids,
            }
        }

