def _check_response(obj, resp):
    resData = obj._resData(resp)
    hse = obj._get_in_xmlns(obj.ns_url)
    hses = obj._get_all_xmlns(obj.ns_url)
    chkData = hse(resData, 'chkData')
    results = {}
    for n in hses(chkData, 'cd'):
        cdn = hse(n, 'name')
        results[cdn.text] = bool(int(cdn.attrib['avail']))
    return {'checks': results}


def check(obj, things):
    rootElem, d, se = obj._cmd_node('check')
    for t in things:
        se(d, 'name').text = t
    return (rootElem, lambda r: _check_response(obj, r))
