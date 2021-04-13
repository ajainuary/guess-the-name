from typing import List
import rdflib
from rdflib.term import URIRef, Literal


class Entity:
    """A class that represents a node in the graph"""

    def __init__(self, qid, graph):
        self.qid = qid
        self.owner = graph  # Our object is a value
        qres = self.owner.rdfGraph.query(
            ''' SELECT ?o
                WHERE 
                {
                wd:''' + self.qid + ''' rdfs:label ?o.
            }'''
        )
        self.label = [x[0] for x in qres]

    def properties(self):
        qres = self.owner.rdfGraph.query(
            ''' SELECT ?p
                WHERE 
                {
                wd:''' + self.qid + ''' ?p ?o.
                filter not exists {
                wd:''' + self.qid + ''' rdfs:label ?o.
                }
            }'''
        )
        ans = [x[0][36:] for x in qres]
        return ans

    def object(self, property):
        qres = self.owner.rdfGraph.query(
            '''
             select ?value  
            {
                wd:''' + self.qid + '''  wdt:''' + property + ''' ?value.
            } 
            '''
        )
        ans = [x[0][31:] if isinstance(
            x[0], rdflib.term.URIRef) else x[0] for x in qres]
        return ans

    def add(self, property, object):
        if isinstance(object, Entity):
            # Our object is an entity
            self.owner.rdfGraph.add((URIRef('http://www.wikidata.org/entity/'+self.qid), URIRef(
                'http://www.wikidata.org/prop/direct/'+property), URIRef('http://www.wikidata.org/entity/'+object.qid)))
        else:
            # Our object is a value
            self.owner.rdfGraph.add((URIRef('http://www.wikidata.org/entity/'+self.qid), URIRef(
                'http://www.wikidata.org/prop/direct/'+property), Literal(object)))
        return False


class Graph:
    """A wrapper for the rdflib.Graph"""

    def __init__(self, rdfGraph: rdflib.Graph):
        self.rdfGraph = rdfGraph
        self.sampledGraph = None

    def nodes(self):
        qres = self.rdfGraph.query("""SELECT distinct ?item
        WHERE
        {
          ?item ?p ?o.
          filter (regex(str(?item), "Q"))
        }"""
                                   )
        ans = []
        for row in qres:
            ans.append(Entity(row[0][31:], self))
        return ans

    def sample_graph(self):
        result = self.rdfGraph.query("""
        CONSTRUCT {
            ?item1 ?p1 ?item.
            ?item rdfs:label ?itemLabel.
            ?item1 rdfs:label ?item1Label.
        }
        WHERE
        {
            Values (?category) {(wd:Q5) (wd:Q3624078) (wd:Q515)}
            ?item wdt:P31 ?category.
        
            ?item1 ?p1 ?item.
            ?item1 wdt:P31 ?category.
        
            ?item rdfs:label ?itemLabel.
            ?item1 rdfs:label ?item1Label.

        }
        """)
        self.sampledGraph = rdflib.Graph()
        self.sampledGraph.bind("wd", rdflib.term.URIRef(
            'http://www.wikidata.org/entity/'))
        for row in result:
            self.sampledGraph.add(row)
        self.sampledGraph = Graph(self.sampledGraph)
