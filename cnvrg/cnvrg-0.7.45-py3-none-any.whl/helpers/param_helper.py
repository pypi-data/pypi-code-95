def wrap_string_to_list(payload):
    if payload == None: return None
    if isinstance(payload, str): payload = [payload]
    return payload

def wrap_into_list(payload):
    if payload == None: return []
    if isinstance(payload, list): return payload
    return [payload]