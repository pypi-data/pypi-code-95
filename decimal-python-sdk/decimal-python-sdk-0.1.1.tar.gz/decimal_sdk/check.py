import hashlib
import rlp
import ethereum.transactions as crypto


class Check:
    chain_id: str
    coin: str
    amount: int
    nonce: bytearray
    due_block: int
    lock: int
    v: int
    r: int
    s: int

    def get_sender(self):
        return self.recover_plain(self.check_hash(), self.r, self.s, self.v)

    def lock_pub_key_(self):
        sig = self.lock.to_bytes()
        if len(sig) < 65:
            sig = 65-len(sig) + int(sig)

        check_hash = self.hash_without_lock()
        pub = crypto.ecrecover_to_pub(check_hash, sig)

        if len(pub) == 0 or pub[0] != 4:
            raise Exception("Invalid public key")

        return pub

    def hash_without_lock(self):
        return self.rpl_hash(
            [
                self.chain_id,
                self.coin,
                self.amount,
                self.nonce,
                self.due_block
            ]
        )

    def check_hash(self):
        return self.rpl_hash(
            [
                self.chain_id,
                self.coin,
                self.amount,
                self.nonce,
                self.due_block,
                self.lock
            ]
        )

    def hash_full(self):
        return self.rpl_hash(
            [
                self.chain_id,
                self.coin,
                self.amount,
                self.nonce,
                self.due_block,
                self.lock,
                self.v,
                self.r,
                self.s
            ]
        )

    def sign(self, prvt_key):
        h = self.check_hash()
        sig = crypto.ecsign(h[:], prvt_key)
        self.set_signature(sig)

    def set_signature(self, sig: bytearray):
        self.r = sig[0:32]
        self.s = sig[32:64]
        self.v = int((sig[64] + 27).to_bytes())

    def recover_plain(self, sighash, r, s, v):
        pass

    @staticmethod
    def parse_check(buf):
        check: Check = rlp.decode(buf)
        if check.s == 0 or check.r == 0 or check.v == 0:
            raise Exception("Incorrect tx signature")

        return check

    @staticmethod
    def rpl_hash(data):
        return hashlib.sha3_256(data)

    def __str__(self):
        return f"Check sender: {self.get_sender()} nonce: {self.nonce}, " \
               f"dueBlock: {self.due_block}, value: {self.amount} {self.coin}"