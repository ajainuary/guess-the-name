import json
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate

import networkx as nx
import dash_cytoscape as cyto
import pickle
import rdflib
import urllib
from rdflib import URIRef

from wrapper import Entity, Graph
from functools import reduce
from copy import deepcopy
from SPARQLWrapper import SPARQLWrapper, JSON
from time import sleep
import os.path
from os import path

# Object declaration
basic_elements = []
nodes = []
edges = []
all_nodes =[]
all_properties = []
dense_graph = Graph()
item = "नरेन्द्र मोदी"
graph_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'width': "20%",
            'height': "20%",
            'font-size': '0.5em'
        }
    },
    {
        "selector": 'edge',
        "style": {
            "target-arrow-color": "#C5D3E2",
            'label': 'data(label)',
            "target-arrow-shape": "triangle",
            "line-color": "#C5D3E2",
            'arrow-scale': 1,
            'font-size': '0.5em',
            # 'width':100,
            # Default curve-If it is style, the arrow will not be displayed, so specify it
            'curve-style': 'bezier'
        }
    },
    {"selector": 'cytoscape',
     "style": {
         # 'height': '95vh',
         'align-content': 'center',
     }
     },
    {"selector": "container",
     "style": {
         'position': 'fixed',
         'display': 'flex',
         'flex-direction': 'column',
     }}
]

def get_graph(item):
    endpointUrl = 'https://query.wikidata.org/sparql'
    # item = '"महात्मा गांधी"'
    itemstring = "'" + item + "'"
    query = '''
        SELECT Distinct ?item
        WHERE { 
        ?item ?label '''+ itemstring+ '''@hi.
        ?item rdfs:label ?itemLabel. filter(lang(?itemLabel) = "hi").
        SERVICE wikibase:label { bd:serviceParam wikibase:language "hi". }
        }
    '''

    sparql = SPARQLWrapper(endpointUrl)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    itemqid = sparql.query().convert()['results']['bindings'][0]['item']['value'][31:]
    
    if(path.exists('original{}Graph'.format(item.replace(" ","")))):
        print("Graph already found")
        return

    print("Extracting Dense Graph")
    itemGraph = rdflib.Graph()
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
    VALUES (?item) {(wd:''' + itemqid + ''')}
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
    result = itemGraph.parse(url)
    print('There are ', len(result), ' triples about item ', item)
    g = Graph(itemGraph)
    print("Saving in file original{}Graph".format(item.replace(" ","")))
    dbfile = open('original{}Graph'.format(item.replace(" ","")), 'wb')
    pickle.dump(g, dbfile)
    dbfile.close()

    print("Extracting Sampled Graph")
    result = g.rdfGraph.query("""
        CONSTRUCT {
            ?item1 ?p1 ?item.
            ?item rdfs:label ?itemLabel.
            ?item1 rdfs:label ?item1Label.
        }
        WHERE
        {
            #   (wd:Q6256)
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
    sampledGraph.bind("wdt", rdflib.term.URIRef(
        'http://www.wikidata.org/prop/direct/'))
    sampledGraph.bind("wikibase", rdflib.term.URIRef(
        'http://wikiba.se/ontology#'))
    print('There are ', len(result), ' triples about item ', item)
    for row in result:
        sampledGraph.add(row)
    sg = Graph(sampledGraph)
    print("Saving in file sampled{}Graph".format(item.replace(" ","")))
    dbfile = open('sampled{}Graph'.format(item.replace(" ","")), 'wb')
    pickle.dump(sg, dbfile)
    dbfile.close()

def get_nodes(graph):
    # print(graph)
    entities = graph.nodes()
    # print(entities[0].label)
    # print(entities[0].label[0])
    return list(map(lambda e: {'label': str(e.label[0]), 'value': e.qid}, entities))


def get_properties(graph):
    ans = []
    for e in graph.nodes():
        props, propsLabel = e.properties()
        ans.extend(list(map(lambda p, pLabel: {'label': str(pLabel[0]), 'value': p}, props, propsLabel)))
    return ans


def get_nodes_display(graph):
    # print(graph)
    entities = graph.nodes()
    return list(map(lambda e: {'data': {'id': str(e.qid), 'label': str(e.label[0])}}, entities))


def get_properties_display(graph):
    # print(graph)
    ans = []
    # print("Printing sampled graph edges")
    for e in graph.nodes():
        # print(e.qid)
        props, propsLabel = e.properties()
        for p in props:
            # print(p)
            value = e.object(p)
            # print(value)
            entities = [graph.get_node(v) for v in value]
            for v in entities:
                ans.append({'data': {
                    'id': p,
                    'source': e.qid,
                    'target': v.qid,
                    'label': p
                }
                })

    return ans
    # return list(map(lambda e: {'data': {'id': str(e.label[0]), 'label': str(e.label[0])}}, entities))


def wiki_exists(graph, e1, p, e2):
    # print(e1)
    # print(p)
    # print(e2)
    qres = graph.rdfGraph.query(
        '''
             select ?value  
            {
                wd:''' + e1 + '''  wdt:''' + p + ''' ?value.
            } 
            '''
    )
    ans = [x[0][31:] if isinstance(
        x[0], rdflib.term.URIRef) else x[0] for x in qres]
    return e2 in ans


def filter_edits(edges):
    return list(filter(lambda x: x['data']['id'][:9] == "SUGG_EDGE", edges))


def score(graph, edges):
    # edits = filter_edits(edges)
    edits = edges
    return reduce(lambda x, y: x+1 if y else x, map(lambda x: wiki_exists(graph, x['data']['source'], x['data']['id'],
                                                                   x['data']['target']), edits), 0)

def get_new_suggestions(edges):
    global dense_graph
    x = list(map(lambda x: wiki_exists(dense_graph, x['data']['source'], x['data']['id'], x['data']['target']), edges))
    # print(x)
    res = []
    k = [edges[v] for v in range(len(x)) if not x[v]]
    for x in k:
        if x not in res:
            res.append(x)
    return res


def gen_interface(item):
    global all_nodes,all_properties,dense_graph
    get_graph(item)
    dbfile = open('original{}Graph'.format(item.replace(" ","")), 'rb')
    dense_graph = pickle.load(dbfile)
    all_nodes = get_nodes(dense_graph)
    all_properties = get_properties(dense_graph)
    dbfile.close()

    dbfile2 = open('sampled{}Graph'.format(item.replace(" ","")), 'rb')
    sg = pickle.load(dbfile2)
    dbfile2.close()
    nodes = get_nodes_display(sg)
    return nodes


dbfile3 = open('allProperties', 'rb')
allprops1 = pickle.load(dbfile3)
dbfile3.close()
all_wiki_properties = list(map(lambda p: {'label': str(p['propertyLabel']['value']), 'value': p['property']['value'][31:]}, allprops1))



styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'},
    
}


layout = html.Div(className="container", children=[
    html.Div([html.H1("Guess the Name")],
             className="row",
             style={'textAlign': "center"}),
    html.Div([html.H2('Final Score :')],
            id ='body-div',
             className="row",
             style={'textAlign': "center",'color':'green'}),
    html.Div([html.H2('Topic Selected :')],
            id ='graph-body-div',
             className="row",
             style={'textAlign': "center",'color':'red'}),

    
    html.Div(className='row', children=[
        html.Div(className='four columns', children=[

        dcc.Input(id='GraphGen', type='text', debounce=True,
                  placeholder='Topic'),
        
        html.Button('Generate Graph', id='btn-gen-graph', n_clicks_timestamp=0),
        
    ]),

        html.Div(className='eight columns', children=[
            cyto.Cytoscape(
                id='cytoscape',
                elements=basic_elements,
                layout={'name': 'cose'},
                stylesheet=graph_stylesheet,
                style={'width': '100%', 'height': '550px',}
            )
        ]),
    ]),
    
    html.Div(className='two columns', children=[
        dcc.Dropdown(
            id='NodeList',
            options=all_nodes,
            # value=all_nodes[0]['value'],
            multi=False,
            placeholder="Select a node"
        )]),

    html.Div(className='row', children=[
        html.Button('Add Node', id='btn-add-node', n_clicks_timestamp=0),
        html.Button('Remove Node', id='btn-remove-node', n_clicks_timestamp=0)
    ]),
    html.Div(id='placeholder'),

    html.Div(className='two columns', children=[
        dcc.Dropdown(
            id='SourceList',
            options=all_nodes,
            # value=all_nodes[0]['value'],
            multi=False,
            placeholder="Select source node"
        )]),

    html.Div(className='two columns', children=[
        dcc.Dropdown(
            id='EdgeList',
            options=all_properties,
            # value=all_properties[0]['value'],
            multi=False,
            placeholder="Select property"
        )]),

    html.Div(className='two columns', children=[
        dcc.Dropdown(
            id='TargetList',
            options=all_nodes,
            # value=all_nodes[0]['value'],
            multi=False,
            placeholder="Select target node"
        )]),

    html.Div([
        html.Button('Add Edge', id='btn-add-edge', n_clicks_timestamp=0),
        html.Button('Remove Edge', id='btn-remove-edge', n_clicks_timestamp=0)
    ]),

    

        html.Div(className='three columns',children=[
            dcc.Input(id='NewSourceList', type='text', debounce=True,
                  placeholder='Add New Source Node'),]),
        # html.Div(),
        html.Div(className="three columns",children=[
            dcc.Dropdown(
            id='NewEdgeList',
            options=all_wiki_properties,
            # value=all_properties[0]['value'],
            multi=False,
            placeholder="Select new property"
        ),]),
        html.Div(className="three columns",children=[dcc.Input(id='NewTargetList', type='text', debounce=True,
                  placeholder='Add New Target Node'),]),
        
    
    html.Div(className="eight columns",children=[html.Button('New Suggestion', 
            id='btn-new-sugg', n_clicks_timestamp=0),html.Button('Remove Suggestion', id='btn-del-sugg',
                    n_clicks_timestamp=0),]),
        
    html.Div(className="two columns",children=[]),
    html.Div(className="sixteen columns",children=[html.A(html.Button('Home'),href='/'),
        html.Button('Reset All', id='btn-rt',n_clicks_timestamp=0),
        html.Button('Submit', id='btn-sub',n_clicks_timestamp=0),
        html.Button('Reset Color', id='btn-reset', n_clicks_timestamp=0), ]),
    
    
    
    html.Div([
        
    ]),

])


def register_callbacks(dashapp, ctx,db,Suggestion):
    @dashapp.callback(Output('cytoscape', 'elements'), [Input('btn-add-node', 'n_clicks'),
                                                        Input(
                                                            'btn-remove-node', 'n_clicks'), Input('btn-add-edge', 'n_clicks'),
                                                        Input(
                                                            'btn-remove-edge', 'n_clicks'), Input('btn-new-sugg', 'n_clicks'),
                                                        Input(
                                                            'btn-del-sugg', 'n_clicks'),Input('btn-sub', 'n_clicks_timestamp'), 
                                                        Input('btn-rt', 'n_clicks'),Input('btn-gen-graph', 'n_clicks'),
                                                        Input('NodeList', 'value'), Input('EdgeList',
                                                                                          'value'), Input('SourceList', 'value'),
                                                        Input('TargetList', 'value'), Input(
                                                            'NewSourceList', 'value'),
                                                        Input('NewEdgeList', 'value'),Input(
                                                            'GraphGen', 'value'), Input(
                                                            'NewTargetList', 'value')
                                                        ])
    def add_delete_node(btn_add_node, btn_remove_node, btn_add_edge, btn_remove_edge, btn_new_sugg, btn_del_sugg,btn_sub,
                        btn_rt,btn_gen_graph,nodeId, edgeId, sourceId, targetId, newSourceId, newEdgeId, newGraphId,newTargetId):
        global nodes
        global edges
        global initial_game_state
        global all_nodes,all_properties,basic_elements,dense_graph,item
        # ctx = dash.callback_context
        if not ctx.triggered:
            return nodes+edges
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            print(button_id)
        ctx_msg = json.dumps({
            'states': ctx.states,
            'triggered': ctx.triggered,
            'inputs': ctx.inputs
        }, indent=2)
        # print(ctx_msg)
        # If the add button was clicked most recently
        # if button_id == 'btn-add-edge':
        #     print(edgeId,sourceId,targetId)
        if button_id == 'btn-add-node':
            print("Node Added")
            nodes.append({'data': {
                'id': str(nodeId),
                'label': [n['label'] for n in all_nodes if n['value'] == str(nodeId)][0],
            }
            })
            return nodes + edges

        # If the remove button was clicked most recently
        elif button_id == 'btn-remove-node':
            nodes = [x for x in nodes if not x['data']['id'] == nodeId]
            return nodes + edges

        # if int(btn_add_edge) > int(btn_remove_edge):
        elif button_id == 'btn-add-edge':
            
            edge_name = "SUGG_EDGE_{}_{}_{}".format(sourceId, edgeId, targetId)
            edges.append({'data': {
                'id': edgeId,
                'source': str(sourceId),
                'target': str(targetId),
                'label': [p['label'] for p in all_properties if p['value'] == str(edgeId)][0]

            }
            })
            s = score(dense_graph, edges) ## Change this to original graph
            return nodes + edges

        elif button_id == 'btn-remove-edge':
            edges = [x for x in edges if not x['data']
                     ['id'] == [e['data']['id'] for e in edges if e['data']['source'] == str(sourceId) and e['data']['target'] == str(targetId)][0]]
            return nodes + edges

        # Neither have been clicked yet (or fallback condition)

        elif button_id == 'btn-new-sugg':
            source_name = 'SUGG_NODE_{}'.format(newSourceId)
            target_name = 'SUGG_NODE_{}'.format(newTargetId)
            edge_name = 'SUGG_EDGE_{}_{}_{}'.format(
                newSourceId, newEdgeId, newTargetId)

            existingTargetID = ""
            existingSourceID = ""

            for n in all_nodes: 
                if str(newTargetId) == n['label']:
                    existingTargetID = n['value']
                if str(newSourceId) == n['label']:
                    existingSourceID = n['value']

            if(existingSourceID == ""):
                existingSourceID = str(newSourceId.replace(" ",""))

            if(existingTargetID == ""):
                existingTargetID = str(newTargetId.replace(" ",""))

            # print("Inside New Suggestion")
            # print(existingSourceID)
            # print(newEdgeId)
            # print(existingTargetID)

            source_node = {'data': {'id': existingSourceID, 'label': newSourceId}}
            target_node = {'data': {'id': existingTargetID, 'label': newTargetId}}
            prop_edge = {'data': {
                'id': newEdgeId,
                'source': str(existingSourceID),
                'target': str(existingTargetID),
                'label': [p['label'] for p in all_wiki_properties if p['value'] == str(newEdgeId)][0]
            }
            }
            print(prop_edge)
            edges.append(prop_edge)

            exists = [x for x in nodes if str(newSourceId) == x['data']['label']]
            if len(exists) == 0:
                nodes.append(source_node)
                graph_stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(existingSourceID),
                    "style": {
                        'background-color': "#FF69B4",
                        # 'opacity': 0.9
                    }
                })
            exists = [x for x in nodes if str(newTargetId) == x['data']['label']]
            if len(exists) == 0:
                nodes.append(target_node)
                graph_stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(existingTargetID),
                    "style": {
                        'background-color': "#FF69B4",
                        # 'opacity': 0.9
                    }
                })

            # s = score(g, edges) ## Change this to original graph
            # print(s)
            # print(edges)

            # print("Suggesting Edges")
            

            return nodes+edges

        elif button_id == 'btn-del-sugg':
            existingTargetID = ""
            existingSourceID = ""

            for n in all_nodes: 
                if str(newTargetId) == n['label']:
                    existingTargetID = n['value']
                if str(newSourceId) == n['label']:
                    existingSourceID = n['value']

            if(existingSourceID == ""):
                existingSourceID = str(newSourceId.replace(" ",""))

            if(existingTargetID == ""):
                existingTargetID = str(newTargetId.replace(" ", ""))
            
            edges = [x for x in edges if not x['data']
                     ['id'] == [e['data']['id'] for e in edges if e['data']['source'] == str(existingSourceID) and e['data']['target'] == str(existingTargetID)][0]]
            
            nodes = [x for x in nodes if not x['data']['id'] == newSourceId]
            nodes = [x for x in nodes if not x['data']['id'] == newTargetId]
            return nodes + edges

        elif button_id == 'btn-rt':
            nodes = initial_game_state
            edges = []
        elif button_id == 'btn-sub':
            new_sugg = get_new_suggestions(edges)
            # print(nodes)
            # print(edges)
            
            for edit in new_sugg:
                label = ""
                k1,k2,k3,k4 = edit['data']['source'],edit['data']['label'],edit['data']['target'],edit['data']['id']
                if 'Q' == k1[0]:
                    for node in nodes:
                        if node['data']['id'] == k1:    
                            label = node['data']['label']
                else:
                    label = k1
                
                edit_name = '{}_{}_{}_{}'.format(label,k2,k3,k4)
                new_edit = Suggestion(edit_name)
                # db.session.add(new_edit)
                # db.session.commit()
            nodes = []
            edges = []

        elif button_id == 'btn-gen-graph':
            if newGraphId == '':
                item = "नरेन्द्र मोदी"
            else:
                item = newGraphId
            nodes = gen_interface(item)
            initial_game_state = deepcopy(nodes)
            basic_elements = nodes
            
            return nodes+edges


        return nodes+edges

    @dashapp.callback([Output(component_id='SourceList', component_property='options'),
                        Output(component_id='EdgeList', component_property='options'),
                        Output(component_id='TargetList', component_property='options'),
                        Output(component_id='NodeList', component_property='options')],
    [Input('graph-body-div', 'children')])
    def update_graph(newGraphId):
        sleep(2)
        global all_nodes,all_properties
        print("Source",len(all_nodes),len(all_properties))
        return all_nodes,all_properties,all_nodes,all_nodes
    
    @dashapp.callback(Output(component_id='graph-body-div', component_property='children'),
    [Input('btn-gen-graph', 'n_clicks')])
    def update_output(n_clicks):
        if n_clicks == 1:
            sleep(2)
        global item
        if n_clicks is None:
            raise PreventUpdate
        else:
            return html.H2('Topic Selected : {}'.format(item))

    @dashapp.callback(Output(component_id='body-div', component_property='children'),
    [Input('btn-sub', 'n_clicks')])
    def update_output(n_clicks):
        global edges,dense_graph
        if n_clicks is None:
            raise PreventUpdate
        else:
            return html.H2('Final Score : {}'.format(score(dense_graph,edges)*10))

    @dashapp.callback(Output('cytoscape', 'stylesheet'),
                      [Input('cytoscape', 'tapNode'),
                       Input('btn-new-sugg', 'n_clicks_timestamp'),
                       Input('btn-reset', 'n_clicks')])
    def generate_stylesheet(inp_node, btn_new_sugg, btn_reset):
        global nodes
        global state_node
        if not inp_node:
            return graph_stylesheet
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'btn-reset':
                return graph_stylesheet
            elif button_id == 'btn-new-sugg':
                return graph_stylesheet
            elif button_id == 'btn-gen-graph':
                return graph_stylesheet
        # if state_node['data']['source'] == inp_node['source']:
        #     print("Same node",inp_node)
        #     return graph_stylesheet
        # else:
        #     print(state_node,inp_node)
        #     state_node = inp_node

        follower_color = "red"
        following_color = "blue"
        stylesheet = [{
            "selector": 'node',
            'style': {
                'opacity': 0.3,
                # 'shape': node_shape
            }
        }, {
            'selector': 'edge',
            'style': {
                'opacity': 0.2,
                "curve-style": "bezier",
            }
        }, {
            "selector": 'node[id = "{}"]'.format(inp_node['data']['id']),
            "style": {
                'background-color': '#B10DC9',
                "border-color": "purple",
                "border-width": 2,
                "border-opacity": 1,
                "opacity": 1,

                "label": "data(label)",
                "color": "#B10DC9",
                "text-opacity": 1,
                "font-size": '0.5em',
                'z-index': 9999
            }
        }]

        for edge in inp_node['edgesData']:
            if edge['source'] == inp_node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['target']),
                    "style": {
                        'background-color': following_color,
                        'opacity': 0.9
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                        "mid-target-arrow-color": following_color,
                        "mid-target-arrow-shape": "vee",
                        "line-color": following_color,
                        'opacity': 0.9,
                        'z-index': 5000
                    }
                })

            if edge['target'] == inp_node['data']['id']:
                stylesheet.append({
                    "selector": 'node[id = "{}"]'.format(edge['source']),
                    "style": {
                        'background-color': follower_color,
                        'opacity': 0.9,
                        'z-index': 9999
                    }
                })
                stylesheet.append({
                    "selector": 'edge[id= "{}"]'.format(edge['id']),
                    "style": {
                        "mid-target-arrow-color": follower_color,
                        "mid-target-arrow-shape": "vee",
                        "line-color": follower_color,
                        'opacity': 1,
                        'z-index': 5000
                    }
                })

        return stylesheet
