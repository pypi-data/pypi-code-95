from eppzy.bases import ObjectDoesNotExist, AuthorizationError


def _contact_create_kwargs_deps(contact_info):
    d = contact_info.data.copy()
    del d['roid']
    d['contact_id'] = d.pop('id')
    d['password'] = 'autocopy'
    return d, set()


def _domain_create_kwargs_deps(domain_info):
    d = domain_info.data.copy()
    for k in ('roid', 'host', 'crDate', 'exDate'):
        del d[k]
    # Nominet specifics
    if d.pop('renew_required', None):
        del d['ns']  # This is permitted by the RFC, but not Nominet
        del d['status']
    d['password'] = 'autocopy'
    return d, {('contact', d['registrant'], 'pass')}


def _host_create_kwargs_deps(host_info):
    d = host_info.data.copy()
    del d['roid']
    return d, set()


info_create_map = {
    'contact': _contact_create_kwargs_deps,
    'domain': _domain_create_kwargs_deps,
    'host': _host_create_kwargs_deps
}


class Overlay:
    def __init__(self, rw, ro, create_kwargs_deps, ensure_deps):
        self._rw = rw
        self._ro = ro
        self._create_kwargs_deps = create_kwargs_deps
        self._ensure_deps = ensure_deps

    def info(self, *a, **k):
        try:
            return self._rw.info(*a, **k)
        except (ObjectDoesNotExist, AuthorizationError):
            ro_info = self._ro.info(*a, **k)
            create_kwargs, deps = self._create_kwargs_deps(ro_info)
            self._ensure_deps(deps)
            self._rw.create(**create_kwargs)
            return self._rw.info(*a, **k)

    def __getattr__(self, attr):
        return getattr(self._rw, attr)


def overlayed(rw_session, ro_session):
    def ensure_deps(deps):
        for k, *args in deps:
            r[k].info(*args)

    r = {}
    for k in set(rw_session) & set(ro_session) & set(info_create_map):
        r[k] = Overlay(
            rw_session[k], ro_session[k], info_create_map[k], ensure_deps)
    return r
