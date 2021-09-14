from .wallet import Wallet
from decimal_sdk.msgs.base import BaseMsg
from decimal_sdk.types import StdSignMsg, SignMeta, Fee, Coin, Candidate
from decimal_sdk.utils.helpers import get_amount_uni
from decimal_sdk.msgs.msgs import (SendCoinMsg, BuyCoinMsg, CreateCoinMsg, UpdateCoinMsg, SellAllCoinsMsg,
                                   DelegateMsg, UnboundMsg, RedeemCheckMsg,
                                   DeclareCandidateMsg, EditCandidateMsg,
                                   DisableEnableValidatorMsg,
                                   MultysigCreateMsg, MultysigCreateTXMsg, MultysigSignTXMsg, MultisendSend, MultisendCoinMsg,
                                   SubmitProposalMsg, VoteProposalMsg,
                                   SwapRedeemMsg, SwapInitMsg,
                                   NftMintMsg, NftBurnMsg, NftEditMetadataMsg, NftTransferMsg, NftDelegateMsg, NftUnboundMsg
                                   )


class Transaction:
    fee: Fee
    memo: str
    meta: SignMeta
    signatures = []
    msgs = []
    signer: StdSignMsg
    message: BaseMsg

    def __init__(self, **kwargs):
        self.meta = SignMeta()
        self.fee = Fee([], '0')
        self.memo = ''
        self.signer = StdSignMsg(self, meta=self.meta)
        self.signer.add_msg(self.message)

    def add_msg(self, msg: BaseMsg):
        self.msgs.append(msg)

    def sign(self, wallet: Wallet):
        self.signer.sign(wallet)
        self.signatures = self.signer.signatures


class SendCoinTransaction(Transaction):
    message: SendCoinMsg

    def __init__(self, sender, receiver, denom, amount, **kwargs):
        coin = Coin(denom, get_amount_uni(amount))
        self.message = SendCoinMsg(sender, receiver, coin)
        super().__init__(**kwargs)


class BuyCoinTransaction(Transaction):
    message: BuyCoinMsg

    def __init__(self, sender, coin_to_buy, coin_to_spend, amount_to_buy, limit=100000000000, **kwargs):
        coin_to_buy = Coin(coin_to_buy, get_amount_uni(amount_to_buy))
        max_coin_to_sell = Coin(coin_to_spend, get_amount_uni(limit))
        self.message = BuyCoinMsg(sender, coin_to_buy, max_coin_to_sell)
        super().__init__(**kwargs)


class CreateCoinTransaction(Transaction):
    message: CreateCoinMsg

    def __init__(self, sender, title, symbol, crr, initial_volume, initial_reserve, identity, limit_volume, **kwargs):
        self.message = CreateCoinMsg(sender, title, symbol, crr, initial_volume, initial_reserve, identity, limit_volume)
        super().__init__(**kwargs)


class UpdateCoinTransaction(Transaction):
    message: UpdateCoinMsg

    def __init__(self, sender, symbol, identity, limit_volume, **kwargs):
        self.message = UpdateCoinMsg(sender, symbol, identity, limit_volume)
        super().__init__(**kwargs)


class SellAllCoinsMsgTransaction(Transaction):
    message: SellAllCoinsMsg

    def __init__(self, sender: str, coin_to_sell_denom: str, coin_to_sell_amount: int, min_coin_to_buy_denom: str,
                 min_coin_to_buy_amount=0, **kwargs):
        coin_to_sell_amount = str(get_amount_uni(coin_to_sell_amount))
        coin_to_sell = Coin(coin_to_sell_denom, coin_to_sell_amount)
        if min_coin_to_buy_amount == 0:
            min_coin_to_buy_amount = 1 #str(get_amount_uni(1))
        else:
            min_coin_to_buy_amount = str(get_amount_uni(min_coin_to_buy_amount))
        min_coin_to_buy = Coin(min_coin_to_buy_denom, min_coin_to_buy_amount)
        self.message = SellAllCoinsMsg(sender, coin_to_sell, min_coin_to_buy)
        super().__init__(**kwargs)


class DelegateTransaction(Transaction):
    message: DelegateMsg

    def __init__(self, delegator_address: str, validator_address: str, denom: str, amount: str, **kwargs):
        coin = Coin(denom, amount)
        self.message = DelegateMsg(delegator_address, validator_address, coin)
        super().__init__(**kwargs)


class UnbondTransaction(Transaction):
    message: UnboundMsg

    def __init__(self, delegator_address: str, validator_address: str, denom: str, amount: str, **kwargs):
        coin = Coin(denom, amount)
        self.message = UnboundMsg(delegator_address, validator_address, coin)
        super().__init__(**kwargs)


class RedeemCheckTransaction(Transaction):
    message: RedeemCheckMsg

    def __init__(self, sender, check, proof, **kwargs):
        self.message = RedeemCheckMsg(sender, check, proof)
        super().__init__(**kwargs)


class DeclareCandidateTransaction(Transaction):
    message: DeclareCandidateMsg

    def __init__(self, commission: int, validator_addr: str, reward_addr: str,
                 denom: str, amount: int,
                 moniker: str, identity: str, website: str, security_contact: str, details: str,
                 key_value: str, key_type: str = 'tendermint/PubKeyEd25519', **kwargs):
        stake = Coin(denom, str(amount))
        pub_key = {"type": key_type, "value": key_value}
        commission = '%.18f' % int(commission)
        description = Candidate(moniker, identity, website, security_contact, details)
        self.message = DeclareCandidateMsg(commission, validator_addr, reward_addr, pub_key, stake, description)
        super().__init__(**kwargs)


class EditCandidateTransaction(Transaction):
    message: EditCandidateMsg

    def __init__(self, validator_address: str, reward_address: str,
                 moniker: str, identity: str, website: str, security_contact: str, details: str, **kwargs):
        description = Candidate(moniker, identity, website, security_contact, details)
        self.message = EditCandidateMsg(validator_address, reward_address, description)
        super().__init__(**kwargs)


class DisableEnableValidatorTransaction(Transaction):
    message: DisableEnableValidatorMsg

    def __init__(self, set_state: str, validator_address: str, **kwargs):
        self.message = DisableEnableValidatorMsg(set_state, validator_address)
        super().__init__(**kwargs)


class MultysigCreateTransaction(Transaction):
    message: MultysigCreateMsg

    def __init__(self, sender: str, owners: list, weights: list, threshold: int, **kwargs):
        self.message = MultysigCreateMsg(sender, owners, weights, threshold)
        super().__init__(**kwargs)


class MultysigCreateTXTransaction(Transaction):
    message: MultysigCreateTXMsg

    def __init__(self, sender: str, wallet: str, receiver: str, denom: str, amount: str, **kwargs):
        coin = Coin(denom, amount)
        self.message = MultysigCreateTXMsg(sender, wallet, receiver, coin)
        super().__init__(**kwargs)


class MultysigSignTXTransaction(Transaction):
    message: MultysigSignTXMsg

    def __init__(self, sender: str, tx_id: str, **kwargs):
        self.message = MultysigSignTXMsg(sender, tx_id)
        super().__init__(**kwargs)


class MultisendCoinTransaction(Transaction):
    message: MultisendCoinMsg

    def __init__(self, sender: str, sends: [MultisendSend], **kwargs):
        self.message = MultisendCoinMsg(sender, sends)
        super().__init__(**kwargs)


class SubmitProposalTransaction(Transaction):
    message: SubmitProposalMsg

    def __init__(self, content: str, proposer: str, voting_start_block: str, voting_end_block: str, **kwargs):
        self.message = SubmitProposalMsg(content, proposer, voting_start_block, voting_end_block)
        super().__init__(**kwargs)


class VoteProposalTransaction(Transaction):
    message: VoteProposalMsg

    def __init__(self, proposal_id: int, voter: str, option: str, **kwargs):
        self.message = VoteProposalMsg(proposal_id, voter, option)
        super().__init__(**kwargs)


class NftMintTransaction(Transaction):
    message: NftMintMsg

    def __init__(self, denom: str, id: str, sender: str, recipient: str, quantity: int, reserve: int, token_uri: str,
                 allow_mint: bool, **kwargs):
        self.message = NftMintMsg(denom, id, sender, recipient, quantity, reserve, token_uri, allow_mint)
        super().__init__(**kwargs)


class NftBurnTransaction(Transaction):
    message: NftBurnMsg

    def __init__(self, denom: str, id: str, sender: str, sub_token_ids: [], **kwargs):
        self.message = NftBurnMsg(denom, id, sender, sub_token_ids)
        super().__init__(**kwargs)


class NftEditMetadataTransaction(Transaction):
    message: NftEditMetadataMsg

    def __init__(self, denom: str, id: str, sender: str, token_uri: str, **kwargs):
        self.message = NftEditMetadataMsg(denom, id, sender, token_uri)
        super().__init__(**kwargs)


class NftTransferTransaction(Transaction):
    message: NftTransferMsg

    def __init__(self, denom: str, id: str, sender: str, recipient: str, sub_token_ids: [], **kwargs):
        self.message = NftTransferMsg(denom, id, sender, recipient, sub_token_ids)
        super().__init__(**kwargs)


class NftDelegateTransaction(Transaction):
    message: NftDelegateMsg

    def __init__(self, denom: str, id: str, delegator_address: str, validator_address: str, sub_token_ids: [], **kwargs):
        self.message = NftDelegateMsg(denom, id, delegator_address, validator_address, sub_token_ids)
        super().__init__(**kwargs)


class NftUnboundTransaction(Transaction):
    message: NftUnboundMsg

    def __init__(self, denom: str, id: str, delegator_address: str, validator_address: str, sub_token_ids: [], **kwargs):
        self.message = NftUnboundMsg(denom, id, delegator_address, validator_address, sub_token_ids)
        super().__init__(**kwargs)


class SwapRedeemTransaction(Transaction):
    message: SwapRedeemMsg

    def __init__(self, sender: str, sent_from: str, recipient: str, amount: int, token_name: str, token_symbol: str,
                 from_chain: str, dest_chain: str, v: str, r: str, s: str, **kwargs):
        self.message = SwapRedeemMsg(sender, sent_from, recipient, str(amount), token_name, token_symbol, from_chain, dest_chain, v, r, s)
        super().__init__(**kwargs)


class SwapInitTransaction(Transaction):
    message: SwapInitMsg

    def __init__(self, sender: str, recipient: str, amount: int, token_symbol: str, from_chain: str, dest_chain, **kwargs):
        self.message = SwapInitMsg(sender, recipient, str(amount), token_symbol, from_chain, dest_chain)
        super().__init__(**kwargs)