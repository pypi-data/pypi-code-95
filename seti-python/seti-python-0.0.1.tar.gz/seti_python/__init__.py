
import execjs
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from base64 import b64decode, b64encode
import json
class MyException(Exception):
    pass



class Seti():
    
    def __init__(self,path_to_private_key:str,api_key:str,public_key='') -> (None):
        self.private_key =path_to_private_key
        self.api_key= api_key
        self.public_key_loc = public_key
    
    def verify_sign(self,signature:str, data:dict):
        '''
        Verifies with a public key from whom the data came that it was indeed 
        signed by their private key
        param: public_key_loc Path to public key
        param: signature String signature to be verified
        return: Boolean. True if the signature is valid; False otherwise. 
        '''
        if self.public_key_loc == '':
            raise MyException({'msg':'Provide public key path','code':1})
        buffered_data = execjs.eval("Buffer.from(JSON.stringify({}))".format(data))
        bytesData = bytearray(buffered_data['data'])
        pub_key = open(self.public_key_loc, "r").read()
        rsakey = RSA.importKey(pub_key)
        signer = PKCS1_v1_5.new(rsakey)
        digest = SHA256.new()
        digest.update(bytesData)
        if signer.verify(digest, b64decode(signature)):
            return True
        return False


    def sign_data(self,data: dict):
        '''
        Generate a sign from data with the private key and api_key
        param: private_key Path to private  key
        param: passphrase  api key
        return: Sign data provide
        '''
        buffered_data = execjs.eval("Buffer.from(JSON.stringify({}))".format(data))
        bytesData = bytearray(buffered_data['data'])
        key = open(self.private_key, "r").read()
        rsakey = RSA.importKey(key, self.api_key)
        hash = SHA256.new(bytesData)
        cipher_rsa = PKCS1_v1_5.new(rsakey)
        return b64encode(cipher_rsa.sign(hash)).decode("utf-8")
    
    