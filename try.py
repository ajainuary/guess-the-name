
import rdflib, urllib
from rdflib import URIRef

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
englishName = itemGraph.preferredLabel(MG, lang='en')
print('English name: ', englishName[0][1])

#serialize the graph as Turtle and save it in a file
r = itemGraph.serialize(destination='rdflibOutput.ttl', format='turtle')
# print(itemGraph.serialize(format="turtle"))
