import sys
import rdflib
from rdflib import URIRef, ConjunctiveGraph
from SPARQLWrapper import SPARQLWrapper, JSON, N3, RDF

endpoint_url = "https://query.wikidata.org/sparql"
query = """construct{
  ?q ?realAtt ?ps_.
}
WHERE {
  BIND(wd:Q1001 AS ?q)
  wd:Q1001 ?p1 ?o.
  ?realAtt wikibase:claim ?p1.
  ?realAtt rdfs:label ?attName.
  ?realAtt wikibase:statementProperty ?ps.
  ?o ?ps ?ps_ .
  ?ps_ rdfs:label ?psName.
  FILTER(((LANG(?attName)) = "hi"))
  FILTER(((LANG(?psName)) = "hi"))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "hi". }
}
"""


def get_results(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(RDF)
    return sparql.query()._convertRDF()


# g = rdflib.Graph()
g = ConjunctiveGraph()
g = get_results(endpoint_url, query)
# MG = URIRef('http://www.wikidata.org/entity/Q1001')
# englishName = g.preferredLabel(MG)
# print(englishName)

# print out the entire Graph in the RDF Turtle format
print(g.serialize(format="turtle").decode("utf-8"))
# for s, p, o in g.triples((None,  None, None)):
#     print("{} {} {}".format(s, p, o))