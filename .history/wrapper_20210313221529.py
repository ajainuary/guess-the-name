import rdflib


class Graph:
    """A wrapper for the rdflib.Graph"""

    def __init__(self, rdfGraph: rdflib.Graph) -> Graph:
        self.rdfGraph = rdfGraph

    def nodes():
