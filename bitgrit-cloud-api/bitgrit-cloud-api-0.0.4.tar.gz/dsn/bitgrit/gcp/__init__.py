import hvac
import os
from google.oauth2 import service_account
from google.cloud import storage
import json

vault_client = hvac.Client(url=os.environ.get('VAULT_URL'), verify=False)
vault_client.renew_token()

# ==========================================================
# GCP Settings
# ==========================================================

# Getting gcp-settings data from vault
dataset_microservice_vault = vault_client.secrets.kv.v2.read_secret_version(
    mount_point='common', path='dataset-microservice')["data"]["data"]

gcp_key = json.loads(dataset_microservice_vault["GCP_SERVICE_ACCOUNT_KEY"])

credentials = service_account.Credentials.from_service_account_info(
    gcp_key
)
storage_client = storage.Client(credentials=credentials,
                                project=gcp_key["project_id"])
