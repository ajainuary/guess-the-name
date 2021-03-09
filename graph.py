import sys

import rdflib

from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"
query = """SELECT ?wdLabel ?ps_Label ?wdpqLabel ?pq_Label {
  VALUES (?company) {(wd:Q1001)}
  
  ?company ?p ?statement .
  ?statement ?ps ?ps_ .
  
  ?wd wikibase:claim ?p.
  ?wd wikibase:statementProperty ?ps.
  
  OPTIONAL {
  ?statement ?pq ?pq_ .
  ?wdpq wikibase:qualifier ?pq .
  }
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} ORDER BY ?wd ?statement ?ps_
"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.queryAndConvert()


results = get_results(endpoint_url, query)
print(results)
g = rdflib.Graph()

# result = g.parse(data=results.serialize(format='xml'), format="xml")

# print out the entire Graph in the RDF Turtle format
# print(g.serialize(format="turtle").decode("utf-8"))
