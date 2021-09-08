import keyring
from bertdotconfig import Struct

def get_credential(entry):
  credential_data = keyring.get_credential(entry, None)
  credential = {
    'username': credential_data._username,
    'password': credential_data._password,
  }
  return Struct(credential)