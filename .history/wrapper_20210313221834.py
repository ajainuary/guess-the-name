from typing import List
import rdflib


class Entity:
    """A class that represents a node in the graph"""

    def __init__(self, qid):
        self.qid = qid


class Graph:
    """A wrapper for the rdflib.Graph"""

    def __init__(self, rdfGraph: rdflib.Graph):
        self.rdfGraph = rdfGraph

    def nodes() -> List[Entities]:
