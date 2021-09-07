from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)

def encrypt(s: str):
    return f.encrypt(bytes(s, 'utf-8'))

def decrypt(token):
    return f.decrypt(token).decode('utf-8')