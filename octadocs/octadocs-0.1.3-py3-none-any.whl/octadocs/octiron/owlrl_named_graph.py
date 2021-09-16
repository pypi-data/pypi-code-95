import itertools

from octadocs.conversions import triples_to_quads
from octadocs.types import Triple
from owlrl import OWLRL_Extension
from owlrl.RDFS import rdf_type
from rdflib import BNode, Literal, Namespace, URIRef


class OWLRLExtensionNamedGraph(OWLRL_Extension):
    """OWL RL with inferred triples in a separate graph."""

    graph_name = URIRef('local:inference/owlrl')

    def flush_stored_triples(self) -> None:
        """Store the triples into a named graph."""
        # Remove the previous version of inferences
        self.graph.remove_context(self.graph_name)

        triples = itertools.starmap(
            Triple,
            self.added_triples,
        )
        quads = triples_to_quads(triples, graph=self.graph_name)
        self.graph.addN(quads)

        self.empty_stored_triples()

    def closure(self):
        """
        Generate the closure the graph. This is the real 'core'.

        The processing rules store new triples via the separate method :func:`.Core.store_triple` which stores
        them in the :code:`added_triples` array. If that array is empty at the end of a cycle,
        it means that the whole process can be stopped.

        If required, the relevant axiomatic triples are added to the graph before processing in cycles. Similarly
        the exchange of literals against bnodes is also done in this step (and restored after all cycles are over).
        """
        # Unfortunately, I had to copy-paste the content of `def closure()` from
        # the base class because I had to override the arguments of
        # `self.graph.add()`. See below.
        self.pre_process()

        # Handling the axiomatic triples. In general, this means adding all
        # tuples in the list that forwarded, and those include RDF or RDFS.
        # In both cases the relevant parts of the container axioms should also
        # be added.
        if self.axioms:
            self.add_axioms()

        # Add the datatype axioms, if needed (note that this makes use of the
        # literal proxies, the order of the call is important!
        if self.daxioms:
            self.add_d_axioms()

        self.flush_stored_triples()

        # Get first the 'one-time rules', ie, those that do not need an extra
        # round in cycles down the line
        self.one_time_rules()
        self.flush_stored_triples()

        # Go cyclically through all rules until no change happens
        new_cycle = True
        cycle_num = 0
        while new_cycle:
            # yes, there was a change, let us go again
            cycle_num += 1

            # DEBUG: print the cycle number out
            if self._debug:
                print("----- Cycle #:%d" % cycle_num)

            # go through all rules, and collect the replies (to see whether any
            # change has been done) the new triples to be added are collected
            # separately not to interfere with the current graph yet
            self.empty_stored_triples()

            # Execute all the rules; these might fill up the added triples array
            for t in self.graph:
                self.rules(t, cycle_num)

            # Add the tuples to the graph (if necessary, that is). If any new
            # triple has been generated, a new cycle will be necessary...
            new_cycle = len(self.added_triples) > 0

            for t in self.added_triples:
                # HERE IS THE PLACE where I changed the code. I just added the
                # graph qualifier.
                self.graph.add(t + (self.graph_name, ))

        self.post_process()
        self.flush_stored_triples()

        # Add possible error messages
        if self.error_messages:
            # I am not sure this is the right vocabulary to use for this
            # purpose, but I haven't found anything!
            # I could, of course, come up with my own, but I am not sure that
            # would be kosher...
            ERRNS = Namespace("http://www.daml.org/2002/03/agents/agent-ont#")
            self.graph.bind(
                "err",
                "http://www.daml.org/2002/03/agents/agent-ont#",
            )
            for m in self.error_messages:
                message = BNode()
                self.graph.add((message, rdf_type, ERRNS['ErrorMessage']))
                self.graph.add((message, ERRNS['error'], Literal(m)))
