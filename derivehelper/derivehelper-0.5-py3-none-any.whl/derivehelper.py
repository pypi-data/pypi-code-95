try:
    from nacl import pwhash
except ImportError:
    raise ImportError("This package requires 'pynacl' to be installed.\n'pip install pynacl'")
try:
    from passlib.hash import argon2, scrypt
    from passlib.hash import pbkdf2_sha1 as ps1
    from passlib.hash import pbkdf2_sha256 as ps2
    from passlib.hash import pbkdf2_sha512 as ps5
    from passlib.hash import sha256_crypt as s2c
    from passlib.hash import sha512_crypt as s5c
    from passlib.hash import bcrypt_sha256 as bcs2
    from passlib.hash import bcrypt as bc
except ImportError:
    raise ImportError("This package requires 'pynacl' to be installed.\n'pip install passlib'")
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as pbkdf2
except ImportError:
    raise ImportError("This package requires 'cryptography' to be installed.\n'pip install cryptography'")
try:
    import bcrypt as b
except ImportError:
    raise ImportError("This package requires 'bcrypt' to be installed.\n'pip install bcrypt'")
from enum import Enum, auto
import hashlib
import time
import base64
import secrets
import string

PW_DATASET = string.ascii_letters + string.digits

class KDF_OPTIONS(Enum):
    ARGON2ID = auto()
    ARGON2I = auto()
    BCRYPT = auto()
    PBKDF2HMAC = auto()
    SCRYPT = auto()

def create_pw(password_length: int = 16):
    if type(password_length) != int:
        raise ValueError('Password length must be an integer.')
    return b''.join(secrets.choice(PW_DATASET).encode() for _ in range(password_length))

def create_salt(password: bytes):
    if type(password) != bytes:
        raise ValueError('Password must be in byte form.')
    password_hash0 = hashlib.sha3_256(password).hexdigest()[:6]
    password_hash1 = hashlib.sha3_512(password).hexdigest()[-6:]
    return f'${password_hash0}$${password_hash1}$'.encode()

class Hash:
    def __init__(self, secret):
        self.secret = secret
    
    def get_secret(self):
        return self.secret
    
    def argon2id(self):
        c_a = argon2.using(type='ID')
        return c_a.hash(self.secret)
    
    def argon2i(self):
        c_a = argon2.using(type='I')
        return c_a.hash(self.secret)
    
    def argon2d(self):
        c_a = argon2.using(type='D')
        return c_a.hash(self.secret)

    def bcrypt(self):
        return bc.hash(self.secret)
    
    def pbkdf2_sha1(self):
        return ps1.hash(self.secret)
            
    def pbkdf2_sha256(self):
        return ps2.hash(self.secret)
            
    def pbkdf2_sha512(self):
        return ps5.hash(self.secret)
    
    def scrypt(self):
        return scrypt.hash(self.secret)
    
    def sha256_crypt(self):
        return s2c.hash(self.secret)

    def sha512_crypt(self):
        return s5c.hash(self.secret)
    
    def bcrypt_sha256(self):
        return bcs2.hash(self.secret)

class KDF:
    def __init__(self, password, salt, KDF_function: KDF_OPTIONS = KDF_OPTIONS.ARGON2ID):
        self.KDF_function = KDF_function
        if (KDF_function == KDF_OPTIONS.ARGON2ID or KDF_function == KDF_OPTIONS.ARGON2I) and not len(salt) == 16:
            raise ValueError(f'Salt must be exactly 16 bytes long for {KDF_function}')
        self.password = password
        self.salt = salt
        if type(salt) != bytes:
            raise ValueError('Salt must be in byte form.')
        elif type(password) != bytes:
            raise ValueError('Password must be in byte form.')
    
    def derive(self, desired_bytes=32, extra_args: tuple=(), encode=False):
        if type(extra_args) != tuple:
            raise ValueError('Extra arguments must be a tuple')
        
        if self.KDF_function == KDF_OPTIONS.ARGON2ID:
            key = pwhash.argon2id.kdf(desired_bytes, self.password, self.salt)
        elif self.KDF_function == KDF_OPTIONS.ARGON2I:
            key = pwhash.argon2i.kdf(desired_bytes, self.password, self.salt)
        elif self.KDF_function == KDF_OPTIONS.BCRYPT:
            if len(extra_args) < 1:
                key = b.kdf(self.password, self.salt, desired_bytes, 100)
            else:
                key = b.kdf(self.password, self.salt, desired_bytes, *extra_args)
        elif self.KDF_function == KDF_OPTIONS.PBKDF2HMAC:
            if len(extra_args) < 1:
                _kdf = pbkdf2(hashes.SHA3_512(), desired_bytes, self.salt, 150000)
            else:
                _kdf = pbkdf2(hashes.SHA3_512(), desired_bytes, self.salt, *extra_args)
            key = _kdf.derive(self.password)
        elif self.KDF_function == KDF_OPTIONS.SCRYPT:
            _kdf = Scrypt(self.salt, desired_bytes, n=2**14, r=8, p=1)
            key = _kdf.derive(self.password)
        else:
            raise ValueError('KDF_function is not valid.')
        
        if encode:
            key = base64.b64encode(key).decode()
        return key

def main():
    hashes_to_test = [x for x in dir(Hash) if not x.startswith('__') and not x.startswith('get')]
    print(f'-----Testing {len(hashes_to_test)} Hashes-----\n')
    hash_pw = create_pw(64)
    h = Hash(hash_pw)
    print(f'PW: {hash_pw.decode()}\n')
    start_of_test = time.time()
    for _hash in hashes_to_test:
        print(f"{_hash}: \t{eval(f'h.{_hash}()')}")
    print(f'\nFinished in {time.time() - start_of_test:.2f} seconds.')
    kdfs_to_test = [x for x in KDF_OPTIONS]
    print(f'\n-----Testing {len(kdfs_to_test)} KDFs-----\n')
    start_of_test = time.time()
    for kdf in kdfs_to_test:
        pw = create_pw(64)
        salt = create_pw(16)
        print(f'KDF: {kdf}')
        print(f'PW: {pw.decode()}')
        print(f'SALT: {salt.decode()}')
        d = KDF(pw, salt, kdf)
        start = time.time()
        print(d.derive())
        print(f'Derived in {time.time() - start:.2f} seconds.\n')
    print(f'Finished in {time.time() - start_of_test:.2f} seconds.')

if __name__ == '__main__':
    start_of_script = time.time()
    main()
    print(f'\n-----Script finished in {time.time() - start_of_script:.2f} seconds-----')
