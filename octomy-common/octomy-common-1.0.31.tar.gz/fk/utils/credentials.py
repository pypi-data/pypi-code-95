from pathlib import Path
import json
import sys
import os
import base64
from .utils import merge

# IMPORTANT!!!!!!
# DO NOT PUT REAL CREDENTIALS HERE!
# INSTEAD EDIT credentials.json THAT IS
# AUTOMATICALLY CREATED ON FIRST RUN OF MAIN SCRIPT
default_credentials = {
    "printful-api-key-source": "Get it here: https://firstkissdesign.myshopify.com/admin/apps/3dd87416a3b1e12a9ef3604aaaaf4d1e/dashboard/settings/1526227/store-api",
    "printful-api-key": "REPLACE-WITH-ACTUAL-KEY",
    "printful-api-key-base64": "",
    "printful-api-endpoint": "https://api.printful.com/",
    "shopify-api-key": "",
    "shopify-password": "",
    "shopify-api-version": "",
    "shopify-shared-secret": "",
    "shopify-shop-name": "",
    "webdriver-url": "http://127.0.0.1:4444/wd/hub",
    "webdriver-max-windows": 5,
    "webdriver-wait-time-sec": 10,
    "influx-hostname": "localhost",
    "influx-port": "8086",
    "influx-username": "root",
    "influx-password": "root",
    "influx-dbname": "sales",
    "cache-dir-name": "_cache",
    "n2report-dir-name": "_n2report",
    "n2report-index-name": "index.html",
    "screenshots-dir-name": "_screenshots",
    "screenshots-index-name": "screenshots.html",
    "db-hostname": "localhost",
    "db-port": "5432",
    "db-username": "postgres",
    "db-password": "",
    "db-database": "postgres",
    "shop-id-generator-min": 0,
    "shop-id-generator-max": 25000000000,  # billions
    "shop-id-generator-batch-size": 200,
    "shop-id-thread-count": 300,
    "crawler-socket-timeout": 15,
    "crawler-referer": "https://www.shopify.com/",
    "crawler-user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    # "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
    "crawler-html-parser": "html5lib",
}


# Load credentials from file, making sure to create defaults if no credentials file found
def load_credentials_ba(credentials_fn="credentials.json"):
    credentials_file = Path(credentials_fn)
    # Create a credentials file with defaults if none exists
    if not credentials_file.is_file():
        print(f"Credentials file {credentials_fn} did not exist, creating")
        with open(credentials_fn, "w") as outfile:
            json.dump(default_credentials, outfile, ensure_ascii=False, sort_keys=True, indent=3)
    # Load credentials from file
    credentials = {}
    if not os.path.exists(credentials_fn):
        print(f"ERROR: Could not find {credentials_fn}")
        sys.exit(1)
    with open(credentials_fn, "r") as json_file:
        print(f"Loading credentials from {credentials_fn}")
        try:
            loaded_credentials = json.load(json_file)
        except Exception as e:
            print("")
            print(f"ERROR: parsing json from '{credentials_fn}':")
            print("")
            print(f"	   {e}")
            print("")
            return None
        credentials = merge(default_credentials, loaded_credentials)

    if credentials["printful-api-key"] == default_credentials["printful-api-key"]:
        print(f"NOTICE: {credentials_fn} contains default values for some credentials\n		If there are any authentication error this might be the culprit.")

    # Printify needs printful-api-key base64 encoded, so do that now b64encode
    credentials["printful-api-key-base64"] = str(base64.urlsafe_b64encode(credentials["printful-api-key"].encode("utf-8")).strip(), "utf-8")

    # Print credentials to terminal for reference
    # print('Credentials: ') 	pprint.pprint(credentials)
    return credentials
