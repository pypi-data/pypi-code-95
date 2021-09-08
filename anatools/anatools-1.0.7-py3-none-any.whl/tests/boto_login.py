import boto3
import warnings
import json
import argparse
import subprocess

def get_password(email, cypressfile=False):
        # create a boto3 client to retrieve the password  
    warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")  
    secret = boto3.client(service_name='secretsmanager')
    response = secret.get_secret_value(SecretId=email)
    password = json.loads(response['SecretString'])['password']
    # os.environ("CYPRESS_PASSWORD")=password
    if cypressfile:
        env_file = open("../deckard/cypress.env.json", "w")
        env_json = {
            "EMAIL": email,
            "PASSWORD" : password
        }
        env_file.write(json.dumps(env_json))
        env_file.close()
        print("Generated cypress.env.json file")
    return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Pass in email to get password with boto')
    parser.add_argument('email')
    parser.add_argument('-c', help='Create the cypress env file', action='store_true')
    args = parser.parse_args()
    get_password(args.email, args.c)