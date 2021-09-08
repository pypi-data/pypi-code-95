from pathlib import Path
from subprocess import Popen
import os
import argparse

ROOT_PATH = str(Path(__file__).parent.absolute())
ES_SCRIPT_PATH = Path(ROOT_PATH, 'server/scripts/start_es.sh')
ES_CONFIG_PATH = Path(ROOT_PATH, 'server/elasticsearch-7.9.2/config')


def start_es(es_script_path, logs_path, data_path, es_config_path, http_port, transport_port):
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    p = Popen(["sh",
               es_script_path,
               data_path,
               logs_path,
               es_config_path,
               str(http_port),
               str(transport_port)])
    return p


def main(logs_path, data_path, http_port=9200, transport_port=9300):
    try:
        p = start_es(ES_SCRIPT_PATH,
                     logs_path,
                     data_path,
                     ES_CONFIG_PATH,
                     http_port,
                     transport_port)
        print("ES STARTED ", p.pid)
        return p
    except:
        raise Exception("Could not start search engine.")


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Start ES server.')
    parser.add_argument('es_logs_path',
                        help="Path to the ES logs folder.")
    parser.add_argument('es_data_path',
                        help="Path to the ES data folder.")
    parser.add_argument('es_http_port', default=9200, help="Http port.", required=False)
    parser.add_argument('es_transport_port', default=9300, help="Transport port.", required=False)
    return parser


if __name__ == "__main__":
    parser = get_arg_parser()
    args = parser.parse_args()

    main(args.es_logs_path, args.es_data_path, args.es_http_port, args.es_transport_port)