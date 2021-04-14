#!/usr/bin/python
# -*- coding: utf-8 -*-
import rdflib
import urllib
from rdflib import URIRef
import random
from wrapper import Graph, Entity
import pickle


def get_allnodes(g):
    entities = g.all_nodes()
    # print(entities)
    return entities


def compute_score(edges):
    score = len(edges['existing'])
    return score


def classify_edges(g, edg):
    # Given a graph and a list of edges this function classifies the edges into two category
    # 1. Existing: Edges that are present in extracted graph
    # 2. New: Edges that are not present and could act as an edit

    edges = {}
    edges['existing'] = []
    edges['new'] = []

    for edge in edg:
        if (edge['s'], edge['p'], edge['o']) in g:
            edges['existing'].append(edge)
        elif (edge['s'], edge['p'], None) in g or (edge['s'], None, edge['o']) in g:
            edges['new'].append(edge)

    return edges


# here's the item to be retrieved
item = 'Q1001'

# instantiate a graph to hold the downloaded triples
itemGraph = rdflib.Graph()

# construct the URL for the HTTP GET call
endpointUrl = 'https://query.wikidata.org/sparql'
item = 'Q1001'
query = '''
CONSTRUCT {
  ?item ?predicate ?field.
  ?item rdfs:label ?itemLabel.
  ?property rdfs:label ?propertyLabel.
  ?field rdfs:label ?fieldLabel.

  ?field ?predicate1 ?field1.
  ?property1 rdfs:label ?property1Label.
  ?field1 rdfs:label ?field1Label.

#   ?field1 ?predicate2 ?field2.
#   ?property2 rdfs:label ?property2Label.
#   ?field2 rdfs:label ?field2Label.
}
WHERE {
  VALUES (?item) {(wd:''' + item + ''')}
  ?item ?predicate ?field.
  ?item rdfs:label ?itemLabel. filter(lang(?itemLabel) = "hi").
  ?property wikibase:directClaim ?predicate.
  ?property rdfs:label ?propertyLabel.  filter(lang(?propertyLabel) = "hi").
  ?field rdfs:label ?fieldLabel.  filter(lang(?fieldLabel) = "hi").

  ?field ?predicate1 ?field1.
  ?property1 wikibase:directClaim ?predicate1.
  ?property1 rdfs:label ?property1Label. filter(lang(?property1Label) = "hi").
  ?field1 rdfs:label ?field1Label. filter(lang(?field1Label) = "hi").

#   ?field1 ?predicate2 ?field2.
#   ?property2 wikibase:directClaim ?predicate2.
#   ?property2 rdfs:label ?property2Label. filter(lang(?property2Label) = "hi").
#   ?field2 rdfs:label ?field2Label. filter(lang(?field2Label) = "hi").

  SERVICE wikibase:label { bd:serviceParam wikibase:language "hi". }
}
'''

url = endpointUrl + '?query=' + urllib.parse.quote(query)

# rdflib retrieves the results, parses the triples, and adds them to the graph
result = itemGraph.parse(url)
print('There are ', len(result), ' triples about item ', item)

# for s, p, o in itemGraph.triples((None, None, None)):
#     sl = itemGraph.preferredLabel(URIRef(s), lang='hi')
#     if not sl:
#         sl = s
#     else:
#         sl = sl[0][1]

#     pl = itemGraph.preferredLabel(URIRef(p), lang='hi')
#     if not pl:
#         pl = p
#     else:
#         pl = pl[0][1]

#     ol = itemGraph.preferredLabel(URIRef(o), lang='hi')
#     if not ol:
#         ol = o
#     else:
#         ol = ol[0][1]

#     print('{} {} {}'.format(sl, pl, ol))

# #serialize the graph as Turtle and save it in a file
r = itemGraph.serialize(destination='rdflibOutput.ttl', format='turtle')
# # print(itemGraph.serialize(format="turtle"))

nodes = get_allnodes(itemGraph)
# edges = []

# for s, p, o in itemGraph.triples((None, None, None)):
#     if type(o) is rdflib.term.URIRef:
#       edge = {}
#       edge['s'] = URIRef(s)
#       edge['p'] = URIRef(p)
#       edge['o'] = URIRef(o)
#       edges.append(edge)
#     if type(o) is rdflib.term.Literal:
#       edge = {}
#       edge['s'] = URIRef(s)
#       edge['p'] = URIRef(p)
#       edge['o'] = o
#       edges.append(edge)

# Dummy user input
edges = [{'p': rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#altLabel'), 'o': rdflib.term.Literal('マハトマ・ガンディ', lang='ja'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')},
         {'p': rdflib.term.URIRef('http://www.wikidata.org/prop/direct/P4180'), 'o': rdflib.term.Literal('32', datatype=rdflib.term.URIRef(
             'http://www.w3.org/2001/XMLSchema#string')), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')},
         {'p': rdflib.term.URIRef('http://schema.org/description'), 'o': rdflib.term.Literal(
             'American political leader', lang='en-ca'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')},
         {'p': rdflib.term.URIRef('http://www.wikidata.org/prop/direct/P2635'), 'o': rdflib.term.Literal('5237e24523334846ac1e310fb935f6ee',
                                                                                                         datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')},
         {'p': rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), 'o': rdflib.term.Literal('Mahatma Gandhi', lang='lfn'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')}]

# edges = classify_edges(itemGraph, edges)
# print('Existing: ' + str(len(edges['existing'])))
# print('New: ' + str(len(edges['new'])))

# score = compute_score(edges)
# print('Score: ' + str(score))

for x in itemGraph.predicate_objects():
    print(x)
print(itemGraph.toPython())

g = Graph(itemGraph)

print("\n \n Printing Original Graph")
ans = g.nodes()
for x in ans:
    print(x.qid, x.label[0])
#     props = x.properties()
#     for y in props:
#         print(y, x.object(y))
#     if x.qid == "Q1001":
#         x.add("P31", "dead person")
#         print(x.object("P31"))

print("\n \n Printing Sampled Graph")
# g.sample_graph()
# for x in g.sampledGraph.nodes():
#     print(x.qid, x.label[0])

print("\n\n")
dbfile = open('pickleGraph', 'ab')
pickle.dump(g, dbfile)
dbfile.close()


def sample_graph(g):
    result = g.rdfGraph.query("""
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
    sampledGraph = rdflib.Graph()
    sampledGraph.bind("wd", rdflib.term.URIRef(
        'http://www.wikidata.org/entity/'))
    for row in result:
        sampledGraph.add(row)
    return Graph(sampledGraph)


dbfile2 = open('./interface/app/dashapp1/sampleGraph', 'wb')
x = sample_graph(g)
print(x)
pickle.dump(x, dbfile2)
dbfile2.close()

# dbfile3 = open('./interface/app/dashapp1/originalGraph', 'wb')
# g = pickle.load(dbfile3)
# print(g)
# dbfile3.close()
