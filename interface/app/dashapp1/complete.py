import json
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import dash_cytoscape as cyto
import pickle
import rdflib
from wrapper import Entity, Graph
from functools import reduce

# Object declaration
basic_elements = []
nodes = []
edges = []


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

def get_nodes(graph):
    print(graph)
    entities = graph.nodes()
    print(entities[0].label)
    print(entities[0].label[0])
    return list(map(lambda e: {'label': str(e.label[0]), 'value': e.qid}, entities))


def get_properties(graph):
    ans = []
    for e in graph.nodes():
        props, propsLabel = e.properties()
        ans.extend(list(map(lambda p, pLabel: {'label': str(pLabel[0]), 'value': p}, props, propsLabel)))
    return ans


def get_nodes_display(graph):
    print(graph)
    entities = graph.nodes()
    return list(map(lambda e: {'data': {'id': str(e.qid), 'label': str(e.label[0])}}, entities))


def get_properties_display(graph):
    print(graph)
    ans = []
    print("Printing sampled graph edges")
    for e in graph.nodes():
        print(e.qid)
        props, propsLabel = e.properties()
        for p in props:
            print(p)
            value = e.object(p)
            print(value)
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
    print(e1)
    print(p)
    print(e2)
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
    x = list(map(lambda x: wiki_exists(g, x['data']['source'], x['data']['id'], x['data']['target']), edges))
    print(x)
    return [edges[v] for v in range(len(x)) if not x[v]]

dbfile = open('originalGraph', 'rb')
g = pickle.load(dbfile)
all_nodes = get_nodes(g)
all_properties = get_properties(g)

print(all_properties[0])
print(all_nodes[0])
# print(all_properties)
dbfile.close()

all_wiki_properties = get_properties(g)
dbfile2 = open('sampleGraph', 'rb')
sg = pickle.load(dbfile2)
# print(sg)

nodes = get_nodes_display(sg)
print(nodes)
basic_elements = nodes
# edges = get_properties_display(g)
# print("Printing all edges from sample graph")
# print(edges)
# basic_elements.extend(edges)

# print(basic_elements)
# basic_elements.extend(all_properties)


styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}

# for node in nodes:
#     if 'SUGG_NODE_' in node['data']['label']:
#         graph_stylesheet.append({
#                     "selector": 'node[id = "{}"]'.format(node['data']['id']),
#                     "style": {
#                         'background-color': "#FF69B4",
#                     }
#                 })


layout = html.Div(className="container", children=[
    html.Div([html.H1("Guess the Name")],
             className="row",
             style={'textAlign': "center"}),

    html.Div(className='row', children=[
        html.Div(className='eight columns', children=[
            cyto.Cytoscape(
                id='cytoscape',
                elements=basic_elements,
                layout={'name': 'cose'},
                stylesheet=graph_stylesheet,
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
    html.Div([
        html.Button('Reset', id='btn-reset', n_clicks_timestamp=0),
        # html.Button('Remove Edge', id='btn-remove-edge', n_clicks_timestamp=0)
    ]),

    html.Div(className='eight columns', children=[

        dcc.Input(id='NewSourceList', type='text', debounce=True,
                  placeholder='Add New Source Node'),
        dcc.Dropdown(
            id='NewEdgeList',
            options=all_wiki_properties,
            # value=all_properties[0]['value'],
            multi=False,
            placeholder="Select new property"
        ),
        dcc.Input(id='NewTargetList', type='text', debounce=True,
                  placeholder='Add New Target Node'),
        html.Button('New Suggestion', id='btn-new-sugg', n_clicks_timestamp=0),
        html.Button('Remove Suggestion', id='btn-del-sugg',
                    n_clicks_timestamp=0),
    ]),
    html.A(html.Button('End Game', className='three columns'),
           href='/'),
    html.Button('Reset All', id='btn-rt'),

])


def register_callbacks(dashapp, ctx):
    @dashapp.callback(Output('cytoscape', 'elements'), [Input('btn-add-node', 'n_clicks'),
                                                        Input(
                                                            'btn-remove-node', 'n_clicks'), Input('btn-add-edge', 'n_clicks'),
                                                        Input(
                                                            'btn-remove-edge', 'n_clicks'), Input('btn-new-sugg', 'n_clicks'),
                                                        Input(
                                                            'btn-del-sugg', 'n_clicks'), Input('btn-rt', 'n_clicks'),
                                                        Input('NodeList', 'value'), Input('EdgeList',
                                                                                          'value'), Input('SourceList', 'value'),
                                                        Input('TargetList', 'value'), Input(
                                                            'NewSourceList', 'value'),
                                                        Input('NewEdgeList', 'value'), Input(
                                                            'NewTargetList', 'value')
                                                        ])
    def add_delete_node(btn_add_node, btn_remove_node, btn_add_edge, btn_remove_edge, btn_new_sugg, btn_del_sugg, btn_rt,
                        nodeId, edgeId, sourceId, targetId, newSourceId, newEdgeId, newTargetId):
        global nodes
        global edges

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
            s = score(g, edges) ## Change this to original graph
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
                'label': [p['label'] for p in all_properties if p['value'] == str(newEdgeId)][0]
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
            print(edges)

            print("Suggesting Edges")
            print(get_new_suggestions(edges))

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
            nodes = []
            edges = []

        return nodes+edges

    @dashapp.callback(Output('cytoscape', 'stylesheet'),
                      [Input('cytoscape', 'tapNode'),
                       Input('btn-new-sugg', 'n_clicks_timestamp'),
                       Input('btn-reset', 'n_clicks')])
    def generate_stylesheet(inp_node, btn_new_sugg, btn_reset):
        global nodes
        if not inp_node:
            return graph_stylesheet
        ctx = dash.callback_context
        if ctx.triggered:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if button_id == 'btn-reset':
                return graph_stylesheet
            elif button_id == 'btn-new-sugg':
                return graph_stylesheet

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

                "label": "data(id)",
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
