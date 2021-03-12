
import rdflib, urllib
from rdflib import URIRef
import random

def get_allnodes(g):
  entities = g.all_nodes()
  # for entity in entities:
  #   print(entity)

  return entities

def compute_score(edges):
  score = len(edges['existing'])
  return score

def classify_edges(g, edg):
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
itemGraph=rdflib.Graph()

# construct the URL for the HTTP GET call
endpointUrl = 'https://query.wikidata.org/sparql'
query = '''
CONSTRUCT {
  wd:''' + item + ''' ?p1 ?o.
}
WHERE {
  wd:''' + item + ''' ?p1 ?o.
}
'''

url = endpointUrl + '?query=' + urllib.parse.quote(query)

# rdflib retrieves the results, parses the triples, and adds them to the graph
result = itemGraph.parse(url)
print('There are ', len(result), ' triples about item ', item)
MG = URIRef('http://www.wikidata.org/entity/Q1001')
Name = itemGraph.preferredLabel(MG, lang='hi')
print('name: ', Name[0][1])

#serialize the graph as Turtle and save it in a file
r = itemGraph.serialize(destination='rdflibOutput.ttl', format='turtle')
# print(itemGraph.serialize(format="turtle"))

# count = 0
# for s, p, o in itemGraph.triples((None, None, None)):
#   print('{} {} {}'.format(s,p,o))
#   count += 1
#   if count > 5:
#     break

nodes = get_allnodes(itemGraph)
edges = []

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

edges = [{'p': rdflib.term.URIRef('http://www.w3.org/2004/02/skos/core#altLabel'), 'o': rdflib.term.Literal('マハトマ・ガンディ', lang='ja'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')},
{'p': rdflib.term.URIRef('http://www.wikidata.org/prop/direct/P4180'), 'o': rdflib.term.Literal('32', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')}, 
{'p': rdflib.term.URIRef('http://schema.org/description'), 'o': rdflib.term.Literal('American political leader', lang='en-ca'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')}, 
{'p': rdflib.term.URIRef('http://www.wikidata.org/prop/direct/P2635'), 'o': rdflib.term.Literal('5237e24523334846ac1e310fb935f6ee', datatype=rdflib.term.URIRef('http://www.w3.org/2001/XMLSchema#string')), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')}, 
{'p': rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#label'), 'o': rdflib.term.Literal('Mahatma Gandhi', lang='lfn'), 's': rdflib.term.URIRef('http://www.wikidata.org/entity/Q1001')}]

edges = classify_edges(itemGraph, edges)
print('Existing: ' + str(len(edges['existing'])))
print('New: ' + str(len(edges['new'])))
score = compute_score(edges)
print('Score: ' + str(score))
