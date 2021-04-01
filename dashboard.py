import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import dash_cytoscape as cyto


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Guess the name"
server = app.server

# Object declaration
basic_elements = []
nodes = []
edges = []

G=nx.DiGraph()
# G.add_nodes_from(["a","b","c","d",1,2])
# G.add_edges_from([("a","c"),("c","d"), ("a",1), (1,"d"), ("a",2)])

graph_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'width': "20%",
            'height': "20%"
        }
    },
    {
        "selector": 'edge',
        "style": {
            "target-arrow-color": "#C5D3E2",
            'label':'data(label)',
            "target-arrow-shape": "triangle",
            "line-color": "#C5D3E2",
            'arrow-scale': 1,
            'label_font_size': '1em',
            # 'width':100,
            'curve-style': 'bezier' #Default curve-If it is style, the arrow will not be displayed, so specify it
        }
    },
        {"selector":'cytoscape',
        "style":{
                # 'height': '95vh',
                'align-content': 'center',
                }
            },
        {"selector":"container",
        "style":{
            'position': 'fixed',
            'display': 'flex',
            'flex-direction': 'column',
      }}
]



for node in G.nodes():
    nodes.append({'data': {
                            'id': str(node), 
                            'label': 'Node ' + str(node)
                        }
                    })

index = 0
for edge in G.edges():
    edges.append({'data': {
                                'id': "edge" + str(index), 
                                'source':str(edge[0]), 
                                'target':str(edge[1]),
                                'label': 'edge ' + str(edge[0]) + str(edge[1]) 
                                }
                            })
    index += 1


all_nodes = [{'label': 'Yusuf Pathan', 'value': 'YP'},{'label': 'Irfan Pathan', 'value': 'IP'},\
            {'label': 'India', 'value': 'IND'},{'label': 'Biryani','value':'BIR'}]
all_properties = [{'label': 'Played for', 'value': 'PLAY'},{'label': 'Son of', 'value': 'SON'},\
                    {'label': 'Brother of', 'value': 'BRO'},{'label':'Favourite Food','value':'FOOD'}]

all_wiki_properties = [{'label': 'Played for', 'value': 'PLAY'},{'label': 'Son of', 'value': 'SON'},\
                    {'label': 'Brother of', 'value': 'BRO'},{'label':'Favourite Food','value':'FOOD'},
                    {'label':'Favourite Player','value':'FAVP'},{'label':'Bowling Style','value':'BOWL'},
                    {'label':'Coach of','value':'COACH'}]



basic_elements = nodes
basic_elements.extend(edges)


styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}



app.layout = html.Div(className="container",children=[
    html.Div([html.H1("Guess the Name")],
             className="row",
             style={'textAlign': "center"}),

    html.Div(className='row',children=[
        html.Div(className='eight columns', children=[
            cyto.Cytoscape(
                id='cytoscape',
                elements=basic_elements,
                layout={'name':'cose'},
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

    html.Div(className='row',children=[
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
    
    html.Div(className='two columns', children=[

        dcc.Input(id='NewSourceList', type='text', debounce=True, placeholder='Add New Source Node'),
        dcc.Dropdown(
                id='NewEdgeList',
                options=all_wiki_properties,
                # value=all_properties[0]['value'],
                multi=False,
                placeholder="Select new property"
        ),
        dcc.Input(id='NewTargetList', type='text', debounce=True, placeholder='Add New Target Node'),
        html.Button('New Suggestion', id='btn-new-sugg', n_clicks_timestamp=0),
        ]),
    
])


@app.callback(Output('cytoscape', 'elements'),
              [Input('btn-add-node', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('btn-add-edge', 'n_clicks_timestamp'),
              Input('btn-remove-edge', 'n_clicks_timestamp'),
              Input('btn-new-sugg', 'n_clicks_timestamp'),
              State('NodeList', 'value'),
              State('EdgeList', 'value'),
              State('SourceList', 'value'),
              State('TargetList', 'value'),
              State('NewSourceList', 'value'),
              State('NewEdgeList', 'value'),
              State('NewTargetList', 'value')
              ])
def add_delete_node(btn_add_node, btn_remove_node,btn_add_edge,btn_remove_edge,btn_new_sugg,nodeId,edgeId,sourceId,targetId,newSourceId,newEdgeId,newTargetId):
    global nodes
    global edges

    ctx = dash.callback_context
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
                                'label': 'Node ' + str(nodeId)
                                } 
                    })
        return nodes + edges

    # If the remove button was clicked most recently
    elif button_id == 'btn-remove-node':
        nodes = [x for x in nodes if not x['data']['id'] == nodeId]
        return nodes + edges

    # if int(btn_add_edge) > int(btn_remove_edge):
    elif button_id == 'btn-add-edge':
        
        edge_name = f'{sourceId}_{edgeId}_{targetId}'    
        edges.append({'data': {
                            'id': edge_name, 
                            'source':str(sourceId), 
                            'target':str(targetId),
                            'label': edge_name 
                            }
                    })
        # print(edges)
        return nodes + edges


    elif button_id == 'btn-remove-edge':
        edges = [x for x in edges if not x['data']['id'] == f'{sourceId}_{edgeId}_{targetId}']
        return nodes + edges
    
    # Neither have been clicked yet (or fallback condition)
    

    elif button_id == 'btn-new-sugg':
        source_name = f'SUGG_NODE_{newSourceId}'
        target_name = f'SUGG_NODE_{newTargetId}'
        edge_name = f'SUGG_EDGE_{newSourceId}_{newEdgeId}_{newTargetId}'

        source_node = {'data':{'id': newSourceId,'label': source_name}}
        target_node = {'data':{'id': newTargetId,'label': target_name}}
        prop_edge = {'data': {
                            'id': edge_name, 
                            'source':str(newSourceId), 
                            'target':str(newTargetId),
                            'label': edge_name 
                            }
                    }
        nodes.append(source_node)
        nodes.append(target_node)
        edges.append(prop_edge)

        graph_stylesheet.append({
                "selector": 'node[id = "{}"]'.format(newSourceId),
                "style": {
                    'background-color': "#FF69B4",
                    # 'opacity': 0.9
                }
            })
        graph_stylesheet.append({
                "selector": 'node[id = "{}"]'.format(newTargetId),
                "style": {
                    'background-color': "#FF69B4",
                    # 'opacity': 0.9
                }
            })

        return nodes+edges

    return nodes+edges    

@app.callback(Output('cytoscape', 'stylesheet'),
              Input('cytoscape', 'tapNode'),
              Input('btn-reset', 'n_clicks_timestamp'),
              Input('btn-new-sugg','n_clicks_timestamp')
               )
def generate_stylesheet(inp_node,btn_reset,btn_new_sugg):
    global nodes
    if not inp_node:
        return graph_stylesheet
    ctx = dash.callback_context
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'btn-reset':
            return graph_stylesheet
        # elif button_id == 'btn-new-sugg':
            
        #         return graph_stylesheet

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
            "font-size": 12,
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




if __name__ == '__main__':
    app.run_server(debug=True)