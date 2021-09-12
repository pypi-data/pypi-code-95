# __main__.py

import argparse
import os
import sys

import requests
import loqed

def parse_arguments():
    """Parse command line arguments"""

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Control a LOQED smart lock',
                                     epilog='Visit https://webhooks.loqed.com for more information')
    parser.add_argument('--version', action='version', version=loqed.__version__)

    sgroup = parser.add_argument_group(title='loqed api')
    sgroup.add_argument('-l', '--lock_id',required=True, help='LOQED lock ID')
    sgroup.add_argument('-k', '--lock_api_key', required=True, help='lock api key')
    sgroup.add_argument('-t', '--api_token', required=True, help='api token')
    sgroup.add_argument('-i', '--local_key_id', required=True, help='local key id')
    sgroup.add_argument('-s', '--state', required=True, help='LOCK, UNLOCK, OPEN')
    

    return parser.parse_args()

def main():
    """Main function for pyloqed command line tool"""
    args = parse_arguments()

    if args.lock_id is None:
        print("Error: lock id not specified.")
        sys.exit(1)
    
    if args.lock_api_key is None:
        print("Error: lock api key not specified.")
        sys.exit(1)

    if args.api_token is None:
        print("Error: api token not specified.")
        sys.exit(1)
    
    if args.local_key_id is None:
        print("Error: local key id not specified.")
        sys.exit(1)

    if args.state is None:
        print("Error: state not specified.")
        sys.exit(1)
    
    try:
        if(args.state == 'OPEN'):
            res = loqed.open(args.lock_id, args.lock_api_key, args.api_token, args.local_key_id)
        
        if(args.state == 'LOCK'):
            res = loqed.lock(args.lock_id, args.lock_api_key, args.api_token, args.local_key_id)

        if(args.state == 'UNLOCK'):
            res = loqed.unlock(args.lock_id, args.lock_api_key, args.api_token, args.local_key_id)

    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to LOQED")
        sys.exit(2)
    except requests.exceptions.HTTPError:
        print("Error: Received invalid response")
        sys.exit(3)
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
        sys.exit(4)
    except requests.exceptions.TooManyRedirects:
        print("Error: Too many redirects")
        sys.exit(5)
    except requests.exceptions.RequestException as reqe:
        print("Error: {e}".format(e=reqe))
        sys.exit(6)

    if res.status_code != requests.codes.ok:
        print("General error!")
        sys.exit(8)

if __name__ == "__main__":
    main()