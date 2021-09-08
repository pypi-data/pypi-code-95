import uuid
import time
import hashlib
import json

def get_event_metadata():
    return {
        "run_id": str(uuid.uuid1()),
        "event_id": str(uuid.uuid4())

    }

# python does some pretty pretting to json objects, we have to change the
# separators to have a bare bone stringifying/dumping function, which will match other languages implementations
def generate_md5_hash_from_payload(payload:dict):
    return hashlib.md5(json.dumps(payload, separators=(',', ':')).encode('utf-8')).hexdigest()

def generate_sha256_hash_from_payload(payload:dict):
    return hashlib.sha256(json.dumps(payload, separators=(',', ':')).encode('utf-8')).hexdigest()

def enrich_valid_event(event, version, count):
    metadata = get_event_metadata()
    event['pipeline']['run_id'] = metadata['run_id']

    event['event']['id'] = metadata['event_id']

    event['data']['checksum_md5'] = generate_md5_hash_from_payload(event['data']['payload'])
    event['data']['checksum_sha256'] = generate_sha256_hash_from_payload(event['data']['payload'])

    event['reporter']['version'] = version
    event['reporter']['sequence'] = count
    event['reporter']['timestamp'] = round(time.time())

    return event

    
