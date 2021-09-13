from __future__ import unicode_literals
from __future__ import print_function

import click
import json
import os
import sys

from .uptycs_rest_api import uptycs_rest_call as urest_call
from .__init__ import __version__


click.disable_unicode_literals_warning = True


class UptycsRest(object):
    def __init__(
        self,
        api_json_key=None,
        verify_ssl=True,
        suffix=None,
        api=None,
        method=None,
        post_data_file=None,
        post_data=None,
        download_location=None,
        threat_source_name=None,
        threat_source_description=None,
        threat_data_csv=None,
    ):

        self.api_json_key_data = json.load(open(api_json_key))
        self.verify_ssl = verify_ssl
        self.suffix = ".uptycs.io"
        if suffix:
            self.suffix = suffix

        self.domain = self.api_json_key_data["domain"]
        self.key = self.api_json_key_data["key"]
        self.secret = self.api_json_key_data["secret"]
        self.verify_ssl = verify_ssl
        self.customer_id = self.api_json_key_data["customerId"]
        self.url = "https://" + self.domain + self.suffix
        self.method = method
        self.download_location = download_location
        if post_data:
            self.post_data = json.loads(post_data)
        else:
            self.post_data = post_data
        self.post_data_file = post_data_file
        if post_data_file:
            self.post_data = json.load(open(post_data_file))

        self.api = api
        self.threat_source_name = threat_source_name
        self.threat_source_description = threat_source_description
        self.threat_data_csv = threat_data_csv

    def call_api(self):
        urest = urest_call(
            url=self.url,
            customer_id=self.customer_id,
            key=self.key,
            secret=self.secret,
            api=self.api,
            method=self.method,
            post_data=self.post_data,
            verify_ssl=self.verify_ssl,
            download_location=self.download_location,
            threat_source_name=self.threat_source_name,
            threat_source_description=self.threat_source_description,
            threat_data_csv=self.threat_data_csv,
        )
        urest.rest_api_call()

        if urest.response_content:
            if urest.is_response_json:
                print(
                    json.dumps(
                        json.loads(urest.response_content), indent=4, sort_keys=True
                    )
                )
            else:
                print(urest.response_content)


@click.command()
@click.option("-V", "--version", is_flag=True, help="Output urestapi's version.")
@click.option("-k", "--keyfile", "keyfile", help="Uptycs json key file.")
@click.option(
    "--domainsuffix", "domainsuffix", help="Uptycs Domain Suffix like" " .uptycs.io"
)
@click.option(
    "--enable-ssl/--disable-ssl", default=False, help="verify ssl certificate"
)
@click.option("-m", "--method", type=str, help="restAPI method [GET|POST|PUT|DELETE]]")
@click.option("-a", "--api", type=str, help="API name [/alerts, /assets, etc]")
@click.option("-d", "--postdata", type=str, help="post json data")
@click.option("-D", "--postdatafile", type=str, help="post json data file")
@click.option(
    "-f", "--location", type=str, help="download location for package", default=None
)
@click.option(
    "--threat_source_name", type=str, help="Name of the threatsource", default=None
)
@click.option(
    "--threat_source_description",
    type=str,
    help="description of the threatsource",
    default=None,
)
@click.option(
    "--threat_data_csv", type=str, help="csv file of the threatsource", default=None
)
def cli(
    version,
    keyfile,
    domainsuffix,
    enable_ssl,
    method,
    api,
    postdata,
    postdatafile,
    location,
    threat_source_name,
    threat_source_description,
    threat_data_csv,
):

    if version:
        print("Version:", __version__)
        sys.exit(0)

    if not keyfile:
        print("Keyfile is required to continue\nPlease check --help option")
        sys.exit(1)

    if not os.path.isfile(keyfile):
        print("ERROR: Key file doesnt exists.")
        sys.exit(1)

    if not api:
        print("API is required to continue\nPlease check --help option")
        sys.exit(1)

    if not method:
        print("method is required to continue\nPlease check --help option")
        sys.exit(1)

    if enable_ssl:
        verify_ssl = True
    else:
        verify_ssl = False

    if method.lower() == "post":
        if api.lower().startswith("/threatsources"):
            if (
                not threat_source_name
                or not threat_source_description
                or not threat_data_csv
            ):
                print("With threat source API\nPlease include following")
                print("--threat_source_name, --threat_source_description")
                print("and --threat_data_csv")
                sys.exit(1)
        else:
            if not postdata and not postdatafile:
                print("method post data json continue\nPlease check --help option")
                sys.exit(1)

    if method.lower() == "put":
        if not postdata and not postdatafile:
            print("method post data json continue\nPlease check --help option")
            sys.exit(1)

    if api.startswith("/packageDownloads"):
        if not location:
            print(
                "api call /packageDownloads need download location\ncheck --help option"
            )
            sys.exit(1)

    api_call = UptycsRest(
        api_json_key=keyfile,
        verify_ssl=verify_ssl,
        suffix=domainsuffix,
        api=api,
        method=method,
        post_data=postdata,
        post_data_file=postdatafile,
        download_location=location,
        threat_source_name=threat_source_name,
        threat_source_description=threat_source_description,
        threat_data_csv=threat_data_csv,
    )

    api_call.call_api()


if __name__ == "__main__":
    cli()
