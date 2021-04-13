def get_nodes(graph):
    entities = graph.nodes()
    return list(map(lambda e: {'label': e.label, 'value': e}, entities))


def get_properties(graph):
    props = graph.properties()
    return list(map(lambda p: {'label': p, 'value': p}, props))
