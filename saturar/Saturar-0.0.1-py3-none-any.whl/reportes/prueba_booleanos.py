#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import saturapi

class BOOL(object):

    """Docstring for BOOL. """

    def __init__(self):
        """TODO: to be defined. """
        pass
    def AND(self, c1, c2):
        """TODO: Docstring for and.

        :a: TODO
        :returns: TODO

        """
        res = []
        for c in c1:
            for d in c2:
                if c['text_cod'] == d['text_cod']:
                    res.append(c)
        return res


bool = BOOL()
c = saturapi.SATURAPI()
c.conectar("/home/vbasel/Doctorado/owncloud/saturar/doctorado_valen_2020_respaldo.db")
codigos = c.recuperar_codigos()
c1 = c.recuperar_codificado('1')
for a in codigos:
    c2 = c.recuperar_codificado(a['id_cod'])
    b = bool.AND(c1, c2)
    print(b)
