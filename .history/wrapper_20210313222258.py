from typing import List
import rdflib


class Entity:
    """A class that represents a node in the graph"""

    def __init__(self, qid):
        self.qid = qid

    def exists(property, object):
        if isinstance(object, Entity):
            # SPARQL Query for checking against entity qid
        else:
            # SPARQL Query for checking against a value
        return False

    def add(property, object):
        if isinstance(object, Entity):
            # SPARQL Query for checking against entity qid
            else:
                # SPARQL Query for checking against a value
        return False


class Graph:
    """A wrapper for the rdflib.Graph"""

    def __init__(self, rdfGraph: rdflib.Graph):
        self.rdfGraph = rdfGraph

    def nodes() -> List[Entities]:
