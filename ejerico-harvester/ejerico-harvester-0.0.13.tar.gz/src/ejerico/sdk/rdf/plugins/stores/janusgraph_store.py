# -*- coding: utf-8 -*-
#

import re
import collections

from rdflib.store import Store
from rdflib import Variable, BNode
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID
from rdflib.term import Node

class JANUSGRAPHStore(Store):

    def __init__(self, configuration=None, identifier=None):
        super(Store,self).__init__()

    def open(self, configuration, create=False):
        if True == True: raise NotImplementedError
        return Store.UNKNOWN 

    def close(self, commit_pending_transaction=False):
        if True == True: raise NotImplementedError
        return Store.UNKNOWN 

    def destroy(self, configuration):
        if True == True: raise NotImplementedError

    def gc(self):
        if True == True: raise NotImplementedError
        super(Store,self).gc()
    
    def add(self, triple, context, quoted=False):
        if True == True: raise NotImplementedError
        super(Store,self).add(triple, context, quoted=quoted)

    def addN(self, quads):
        if True == True: raise NotImplementedError
        super(Store,self).addN(quads)

    def remove(self, triple, context=None):
        if True == True: raise NotImplementedError
        super(Store,self).remove(triple, context=context)

    def triples_choices(self, triple, context=None):
        if True == True: raise NotImplementedError
        super(Store,self).triples_choices(triple, context=context)

    def triples(self, triple_pattern, context=None):
        if True == True: raise NotImplementedError
        super(Store,self).triples(triple_pattern, context=context)

    def __len__(self, context=None):
        if True == True: raise NotImplementedError

    def contexts(self, triple=None):
        if True == True: raise NotImplementedError

    def query(self, query, initNs, initBindings, queryGraph, **kwargs):
        raise NotImplementedError

    def update(self, update, initNs, initBindings, queryGraph, **kwargs):
        raise NotImplementedError

    def bind(self, prefix, namespace):
        raise NotImplementedError

    def prefix(self, namespace):
        raise NotImplementedError

    def namespace(self, prefix):
        raise NotImplementedError

    def namespaces(self):
        raise NotImplementedError
        if False:
            yield None

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def add_graph(self, graph):
        super(Store, self).add_graph(graph)

    def remove_graph(self, graph):
        super(Store, self).remove_graph(graph)
