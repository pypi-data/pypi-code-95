from collections import defaultdict
from eppzy.bases import EPPMapping, object_handler, extract_optional


def _get_ots(se, root_elem):
    built_nodes = defaultdict(dict)

    def _ots(parent_elem, val, name, *subnames):
        if val is not None:
            if subnames:
                kids = built_nodes[id(parent_elem)]
                if type(name) is tuple:
                    name, attrib = name
                else:
                    attrib = {}
                n = kids.get(name)
                if not n:
                    n = kids[name] = se(parent_elem, name, attrib=attrib)
                _ots(n, val, *subnames)
            else:
                if type(val) is str:
                    se(parent_elem, name).text = val
                else:
                    for entry in val:
                        se(parent_elem, name).text = entry
    return lambda v, *ns: _ots(root_elem, v, *ns)


@object_handler('contact', 'urn:ietf:params:xml:ns:contact-1.0')
class Contact(EPPMapping):
    def _create_response(self, resp):
        resData = self._resData(resp)
        cse = self._get_in_xmlns(self.ns_url)
        crData = cse(resData, 'creData')
        return {
            'id': cse(crData, 'id').text,
            'date': cse(crData, 'crDate').text
        }

    @staticmethod
    def _add_disclosures(se, p, flag, disclosures):
        if disclosures:
            d = se(p, 'disclose', attrib={'flag': str(flag)})
            for i in disclosures:
                se(d, i, attrib={'type': 'loc'})

    def create(
            self, contact_id, name, city, country_code, email, password,
            org=None, street=[], state_or_province=None, postcode=None,
            voice=None, fax=None, disclose=[], undisclose=[]):
        rootElem, c, se = self._cmd_node('create')
        se(c, 'id').text = contact_id
        p = se(c, 'postalInfo', attrib={'type': 'loc'})
        se(p, 'name').text = name
        if org:
            se(p, 'org').text = org
        a = se(p, 'addr')
        assert type(street) is not str
        for line in street:
            se(a, 'street').text = line
        se(a, 'city').text = city
        if state_or_province:
            se(a, 'sp').text = state_or_province
        if postcode:
            se(a, 'pc').text = postcode
        se(a, 'cc').text = country_code
        if voice:
            se(c, 'voice').text = voice
        if fax:
            se(c, 'fax').text = fax
        se(c, 'email').text = email
        se(se(c, 'authInfo'), 'pw').text = password
        self._add_disclosures(se, c, 1, disclose)
        self._add_disclosures(se, c, 0, undisclose)
        return (rootElem, self._create_response)

    @staticmethod
    def _extract_disclosures(cse, p, flag):
        rv = []
        dn = cse(p, 'disclose[@flag="{}"]'.format(flag))
        if dn is not None:
            for dis in dn:
                rv.append(dis.tag.rsplit('}')[1])
        return rv

    def _info_response(self, resp):
        resData = self._resData(resp)
        cse = self._get_in_xmlns(self.ns_url)
        cses = self._get_all_xmlns(self.ns_url)
        i = cse(resData, 'infData')
        pi = cse(i, 'postalInfo')
        a = cse(pi, 'addr')
        data = {
            'id': cse(i, 'id').text,
            'roid': cse(i, 'roid').text,
            'name': cse(pi, 'name').text,
            'street': [n.text for n in cses(a, 'street')],
            'city': cse(a, 'city').text,
            'country_code': cse(a, 'cc').text,
            'email': cse(i, 'email').text,
            'disclose': self._extract_disclosures(cse, i, 1),
            'undisclose': self._extract_disclosures(cse, i, 0)
        }
        extract_optional(cse, pi, data, 'org')
        extract_optional(cse, a, data, 'sp', dict_name='state_or_province')
        extract_optional(cse, a, data, 'pc', dict_name='postcode')
        extract_optional(cse, i, data, 'voice')
        extract_optional(cse, i, data, 'fax')
        return data

    def info(self, contact_id, password):
        rootElem, c, se = self._cmd_node('info')
        se(c, 'id').text = contact_id
        se(se(c, 'authInfo'), 'pw').text = password
        return (rootElem, self._info_response)

    def update(
            self, contact_id, name=None, org=None, street=None, city=None,
            state_or_province=None, postcode=None, country_code=None,
            voice=None, fax=None, email=None, password=None, disclose=[],
            undisclose=[], localised=True):
        assert type(street) is not str
        rootElem, c, se = self._cmd_node('update')
        se(c, 'id').text = contact_id
        chg = se(c, 'chg')
        o = _get_ots(se, chg)
        pi = ('postalInfo', {'type': 'loc' if localised else 'int'})
        o(name, pi, 'name')
        o(org, pi, 'org')
        o(street, pi, 'addr', 'street')
        o(city, pi, 'addr', 'city')
        o(state_or_province, pi, 'addr', 'sp')
        o(postcode, pi, 'addr', 'pc')
        o(country_code, pi, 'addr', 'cc')
        o(voice, 'voice')
        o(fax, 'fax')
        o(email, 'email')
        o(password, 'authInfo', 'pw')
        self._add_disclosures(se, chg, 1, disclose)
        self._add_disclosures(se, chg, 0, undisclose)
        return (rootElem, lambda r: r)
