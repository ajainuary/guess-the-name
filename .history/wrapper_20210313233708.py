from typing import List
import rdflib


# class Entity:
#     """A class that represents a node in the graph"""

#     def __init__(self, qid, graph):
#         self.qid = qid
#         self.owner = graph  # Our object is a value

#     def exists(property, object) -> bool:
#         if isinstance(object, Entity):
#             # Our object is an entity
#             # SPARQL Query for checking against entity qid
#         else:
#             # Our object is a value
#             # SPARQL Query for checking against a value
#         return False

#     def add(property, object):
#         if isinstance(object, Entity):
#             # Our object is an entity
#             # SPARQL Query for checking against entity qid
#         else:
#             # Our object is a value
#             # SPARQL Query for checking against a value
#         return False


class Graph:
    """A wrapper for the rdflib.Graph"""

    def __init__(self, rdfGraph: rdflib.Graph):
        self.rdfGraph = rdfGraph

    def nodes(self):
        qres = self.rdfGraph.query("""SELECT ?item
        WHERE
        {
          ?item ?p ?o.
          filter (regex(str(?item), "Q"))
        }"""
                                   )
        for row in qres:
            print(row[0][31:])
