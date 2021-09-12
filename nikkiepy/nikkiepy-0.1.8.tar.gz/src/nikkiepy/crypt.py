from cryptography.fernet import Fernet

key = "UHW5VsOL7Hy6h9QaoVNQwSOJqdxXq05RXNWIJf_gA3c="
fer = Fernet(key)

def encrypt(file):
    file = file

    with open(file, 'r') as f:
        read = f.read()

    with open(file, 'w') as f:
        f.write(fer.encrypt(read.encode()).decode())

def decrypt(file):
    file = file

    with open(file, 'r') as f:
        read = f.read()

    with open(file, 'w') as f:
        f.write(fer.decrypt(read.encode()).decode())