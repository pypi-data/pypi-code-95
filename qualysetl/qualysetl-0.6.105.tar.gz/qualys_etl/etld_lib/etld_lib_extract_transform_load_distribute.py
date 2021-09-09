import shelve
import json
import requests
import time
import re
from pathlib import Path
from qualys_etl.etld_lib import etld_lib_functions as etld_lib_functions
from qualys_etl.etld_lib import etld_lib_credentials as etld_lib_credentials
global http_error_codes_v2_api
import qualys_etl

http_error_codes_v2_api = {
    "202": "Retry Later Duplicate Operation.",
    "400": "Bad Request Unrecognized parameter",
    "401": "Unauthorized check credentials",
    "403": "Forbidden User account is inactive or user license not authorized for API. ",
    "409": "Conflict Check Concurrency and Rate Limits",
    "501": "Internal Error. Contact your TAM to open ticket. ",
    "503": "Maintenance we are performing scheduled maintenance on our system.",
}


def get_qualys_headers(request=None):
    # 'X-Powered-By': 'Qualys:USPOD1:a6df6808-8c45-eb8c-e040-10ac13041e17:9e42af6e-c5a2-4d9e-825c-449440445cc8'
    # 'X-RateLimit-Limit': '2000'
    # 'X-RateLimit-Window-Sec': '3600'
    # 'X-Concurrency-Limit-Limit': '10'
    # 'X-Concurrency-Limit-Running': '0'
    # 'X-RateLimit-ToWait-Sec': '0'
    # 'X-RateLimit-Remaining': '1999'
    # 'Keep-Alive': 'timeout=300, max=250'
    # 'Connection': 'Keep-Alive'
    # 'Transfer-Encoding': 'chunked'
    # 'Content-Type': 'application/xml'
    if request is None:
        pass
    else:
        request_url = request.url
        url_fqdn = re.sub("(https://)([0-9a-zA-Z\.\_\-]+)(/.*$)", "\g<2>", request_url)
        url_end_point = re.sub("(https://[0-9a-zA-Z\.\_\-]+)/", "", request_url)
        headers = {}
        if 'X-RateLimit-Limit' in request.headers.keys():
            x_ratelimit_limit = request.headers['X-RateLimit-Limit']
            headers['x_ratelimit_limit'] = x_ratelimit_limit

        if 'X-RateLimit-Window-Sec' in request.headers.keys():
            x_ratelimit_window_sec = request.headers['X-RateLimit-Window-Sec']
            headers['x_ratelimit_window_sec'] = x_ratelimit_window_sec

        if 'X-RateLimit-ToWait-Sec' in request.headers.keys():
            x_ratelimit_towait_sec = request.headers['X-RateLimit-ToWait-Sec']
            headers['x_ratelimit_towait-sec'] = x_ratelimit_towait_sec

        if 'X-RateLimit-Remaining' in request.headers.keys():
            x_ratelimit_remaining = request.headers['X-RateLimit-Remaining']
            headers['x_ratelimit_remaining'] = x_ratelimit_remaining

        if 'X-Concurrency-Limit-Limit' in request.headers.keys():
            x_concurrency_limit_limit = request.headers['X-Concurrency-Limit-Limit']
            headers['x_concurrency_limit_limit'] = x_concurrency_limit_limit

        if 'X-Concurrency-Limit-Running' in request.headers.keys():
            x_concurrency_limit_running = request.headers['X-Concurrency-Limit-Running']
            headers['x_concurrency_limit_running'] = x_concurrency_limit_running

        headers['url'] = request_url
        headers['api_fqdn_server'] = url_fqdn
        headers['api_end_point'] = url_end_point

        return headers


def get_http_error_code_message_v2_api(http_error=""):
    global http_error_codes_v2_api

    if http_error in http_error_codes_v2_api.keys():
        return http_error_codes_v2_api[http_error]
    else:
        return None


def load_json(load_json_file=None, shelve_db=None):
    try:
        with open(load_json_file, "w", encoding='utf-8') as output_json_file:
            output_json_file.write("[")
            with shelve.open(str(shelve_db), flag='r') as shelve_database:
                count_key_value_pairs_loaded_to_json = 0
                shelve_length = len(shelve_database)
                keys_max_count_added_to_json = 1
                for shelve_key in shelve_database:
                    shelve_data = shelve_database[shelve_key]
                    json.dump(shelve_data, output_json_file, indent=4)
                    keys_max_count_added_to_json = keys_max_count_added_to_json + 1
                    count_key_value_pairs_loaded_to_json = count_key_value_pairs_loaded_to_json + 1
                    if keys_max_count_added_to_json > shelve_length:
                        break
                    else:
                        output_json_file.write(",")
            output_json_file.write("]")
    except Exception as e:
        etld_lib_functions.logger.error(f"Error in File: {__file__} Line: {etld_lib_functions.lineno()}")
        etld_lib_functions.logger.error(f"Exception: {e}")
        exit(1)
    return count_key_value_pairs_loaded_to_json


# def extract_json_qualys(
#         try_extract_max_count=3,
#         url=None,
#         headers=None,
#         payload=None,
#         http_conn_timeout=30,
#         chunk_size_calc=20480,
#         json_file=None,
#         cred_dict=None,
#         qualys_headers_dict=None,
#         multi_proc_batch_number=None,
#         extract_validation_type = 'xml'
#
# ):
#
#     for _ in range(try_extract_max_count):
#         try:
#             headers['User-Agent'] = f"qualysetl_v{qualys_etl.__version__}"
#             with requests.request("POST", url, stream=True, headers=headers, data=payload, timeout=http_conn_timeout) as r:
#                 #  TODO: grab header and check concurrent connections information
#                 qualys_headers = get_qualys_headers(r)
#                 if multi_proc_batch_number is None:
#                     qualys_headers_dict['batch_000001'] = get_qualys_headers(r)
#                 else:
#                     qualys_headers_dict[multi_proc_batch_number] = get_qualys_headers(r)
#
#                 etld_lib_functions.logger.info(f"{multi_proc_batch_number}, Qualys Headers: {qualys_headers}")
#                 if r.status_code == 200:
#                     with open(json_file, "w", encoding='utf-8') as f:
#                         for chunk in r.iter_content(chunk_size=chunk_size_calc):
#                             try:
#                                 f.write(chunk.decode('utf-8'))
#                             except Exception as e:
#                                 f.write(etld_lib_functions.remove_low_high_values(chunk).decode('utf-8'))
#                     extract_validation(validation_type=extract_validation_type, output_file_to_validate=output_file)
#                 else:
#                     message = get_http_error_code_message_v2_api(str(r.status_code))
#                     etld_lib_functions.logger.error(f"HTTP USER: {cred_dict['username']} url: {url}")
#                     etld_lib_functions.logger.error(f"HTTP {r.status_code}, exiting. message={message}")
#                     if r.status_code == 401 and extract_validation_type == 'json':
#                         pass
#                         # TODO retest login and if successful, retry, else exit
#                     exit(1)
#
#         except Exception as e:
#             etld_lib_functions.logger.warning(f"Warning for extract file: {Path(json_file).name}")
#             etld_lib_functions.logger.warning(f"Warning {e}")
#             etld_lib_functions.logger.warning(f"Retry attempt number: {_ + 1}")
#             time.sleep(60)
#             continue
#         else:
#             break  # success
#     else:
#         etld_lib_functions.logger.error(f"Max retries attempted: {try_extract_max_count}")
#         etld_lib_functions.logger.error(f"extract file: {Path(json_file).name}")
#         exit(1)


def extract_validation(validation_type='xml', output_file_to_validate=None):
    # TODO Add Logic to validate xml and json
    if 'xml' in validation_type:
        pass
    elif 'json' in validation_type:
        pass

    return True


def extract_qualys(
        try_extract_max_count=3,
        url=None,
        headers=None,
        payload=None,
        http_conn_timeout=30,
        chunk_size_calc=20480,
        output_file=None,
        cred_dict=None,
        qualys_headers_dict=None,
        multi_proc_batch_number=None,
        extract_validation_type='xml'
):

    for _ in range(try_extract_max_count):
        try:
            headers['User-Agent'] = f"qualysetl_v{qualys_etl.__version__}"
            with requests.request("POST", url, stream=True, headers=headers, data=payload, timeout=http_conn_timeout) as r:
                qualys_headers = get_qualys_headers(r)
                if multi_proc_batch_number is None:
                    qualys_headers_dict['batch_000001'] = get_qualys_headers(r)
                else:
                    qualys_headers_dict[multi_proc_batch_number] = get_qualys_headers(r)

                etld_lib_functions.logger.info(f"Qualys Headers: {qualys_headers}")
                if r.status_code == 200:
                    with open(output_file, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size_calc):
                            try:
                                 f.write(chunk)
                            except Exception as e:
                                f.write(etld_lib_functions.remove_low_high_values(chunk).decode('utf-8'))
                    extract_validation(validation_type=extract_validation_type, output_file_to_validate=output_file)
                elif r.status_code == 409 or r.status_code == 202:  # Concurrency Issue or Duplicate Operation.
                    message = get_http_error_code_message_v2_api(str(r.status_code))
                    etld_lib_functions.logger.warning(f"HTTP USER: {cred_dict['username']} url: {url}")
                    raise Exception(f"HTTP Status is: {r.status_code}, message: {message}")
                else:
                    message = get_http_error_code_message_v2_api(str(r.status_code))
                    etld_lib_functions.logger.error(f"HTTP USER: {cred_dict['username']} url: {url}")
                    etld_lib_functions.logger.error(f"HTTP {r.status_code}, exiting. message={message}")
                    exit(1)
        except Exception as e:
            time_sleep = 120
            etld_lib_functions.logger.warning(f"Warning for extract file: {Path(output_file).name}")
            etld_lib_functions.logger.warning(f"Warning {e}")
            etld_lib_functions.logger.warning(f"Sleeping for {time_sleep} seconds before next retry.")
            etld_lib_functions.logger.warning(f"Retry attempt number: {_ + 1}")
            time.sleep(time_sleep)
            continue
        else:
            break  # success
    else:
        etld_lib_functions.logger.error(f"Max retries attempted: {try_extract_max_count}")
        etld_lib_functions.logger.error(f"extract file: {Path(output_file).name}")
        exit(1)
