"""
    Title: encrypt.py
    Author: Himshi C.
    Modified By: Kushagra A.
    Language: Python
    Date Created: 02-09-2021
    Date Modified: 03-09-2021
    Description:
        ###############################################################
        ## Encrypt and decrypt a json file   ## 
         ###############################################################
 """

from cryptography.fernet import Fernet
import os


class Encryptor():

    # encrypting a file
    def encrypt_file(self, key, file_name):
        def get_file_data(filename:str) -> bytes:
            with open(filename, 'r') as fo:
                 data = fo.read()
            return data.encode("utf-8")

        plain_text:bytes = get_file_data(file_name)
        f:"Fernet" = Fernet(key)
        cipher_text = f.encrypt(plain_text)

        with open (file_name + ".enc", 'wb') as fo:
            fo.write(cipher_text)
        os.remove(file_name)
    
    # decrypting a file
    def decrypt_file(self, key, file_name):
        
        f:"Fernet" = Fernet(key)
        with open(file_name, 'rb') as fo:
            cipher_text = fo.read()
        plain_text2 = f.decrypt(cipher_text)

        with open(file_name[:-4], 'wb') as fo:               # opening file in binary mode
            fo.write(plain_text2)
        os.remove(file_name)