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
G.add_nodes_from(["a","b","c","d",1,2])
G.add_edges_from([("a","c"),("c","d"), ("a",1), (1,"d"), ("a",2)])

graph_stylesheet = [
    {
        'selector': 'node',
        'style': {
            'background-color': '#BFD7B5',
            'label': 'data(label)',
            'width': "30%",
            'height': "50%"
        }
    },
    {
        "selector": 'edge',
        "style": {
            "target-arrow-color": "#C5D3E2",
            "target-arrow-shape": "triangle",
            "line-color": "#C5D3E2",
            'arrow-scale': 2,
            'curve-style': 'bezier' #Default curve-If it is style, the arrow will not be displayed, so specify it
        }
    }
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

app.layout = html.Div([
    html.Div(className='sixteen columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=basic_elements,
            stylesheet=graph_stylesheet,
        )
    ]),

    html.Div(className='two columns', children=[
            dcc.Dropdown(
                id='NodeList',
                options=[
                    {'label': 'Yusuf Pathan', 'value': 'YP'},
                    {'label': 'Irfan Pathan', 'value': 'IP'},
                    {'label': 'India', 'value': 'IND'}
                ],
                value='IND',
                multi=False,
                placeholder="Select a node"
        )]),

    html.Div([
    html.Button('Add Node', id='btn-add-node', n_clicks_timestamp=0),
    html.Button('Remove Node', id='btn-remove-node', n_clicks_timestamp=0)
        ]),
    html.Div(id='placeholder'),

    html.Div(className='two columns', children=[
            dcc.Dropdown(
                id='SourceList',
                options=[
                    {'label': 'Yusuf Pathan', 'value': 'YP'},
                    {'label': 'Irfan Pathan', 'value': 'IP'},
                    {'label': 'India', 'value': 'IND'}
                ],
                value='IND',
                multi=False,
                placeholder="Select source node"
        )]),

    html.Div(className='two columns', children=[
            dcc.Dropdown(
                id='EdgeList',
                options=[
                    {'label': 'Played for', 'value': 'PLAY'},
                    {'label': 'Son of', 'value': 'SON'},
                    {'label': 'Brother of', 'value': 'BRO'}
                ],
                value='PLAY',
                multi=False,
                placeholder="Select property"
        )]),
    
    html.Div(className='two columns', children=[
            dcc.Dropdown(
                id='TargetList',
                options=[
                    {'label': 'Yusuf Pathan', 'value': 'YP'},
                    {'label': 'Irfan Pathan', 'value': 'IP'},
                    {'label': 'India', 'value': 'IND'}
                ],
                value='IND',
                multi=False,
                placeholder="Select target node"
        )]),

    html.Div([
    html.Button('Add Edge', id='btn-add-edge', n_clicks_timestamp=0),
    html.Button('Remove Edge', id='btn-remove-edge', n_clicks_timestamp=0)
        ]),
])


@app.callback(Output('cytoscape', 'elements'),
              [Input('btn-add-node', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('btn-add-edge', 'n_clicks_timestamp'),
              Input('btn-remove-edge', 'n_clicks_timestamp'),
              State('NodeList', 'value'),
              State('EdgeList', 'value'),
              State('SourceList', 'value'),
              State('TargetList', 'value')
              ])
def add_delete_node(btn_add_node, btn_remove_node,btn_add_edge,btn_remove_edge,nodeId,edgeId,sourceId,targetId):
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
    if button_id == 'btn-add-edge':
        print(edgeId,sourceId,targetId)
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
        
        edges.append({'data': {
                            'id': f'{sourceId}_{edgeId}_{targetId}', 
                            'source':str(sourceId), 
                            'target':str(targetId),
                            'label': f'{sourceId}_{edgeId}_{targetId}' 
                            }
                    })
        # print(edges)
        return nodes + edges


    elif button_id == 'btn-remove-edge':
        edges = [x for x in edges if not x['data']['id'] == f'{sourceId}_{edgeId}_{targetId}']
        # print(edges)
        return nodes + edges
    
    # Neither have been clicked yet (or fallback condition)
    return nodes+edges


# @app.callback(Output('cytoscape', 'elements'),
#               [Input('btn-add-edge', 'n_clicks_timestamp'),
#               Input('btn-remove-edge', 'n_clicks_timestamp'),
              # State('EdgeList', 'value'),
              # State('SourceList', 'value'),
              # State('TargetList', 'value'),
#               State('cytoscape', 'elements')])
# def add_delete_edge(btn_add, btn_remove, edgeId,sourceid,targetid,elements):
#     global nodes
#     global edges
#     # If the add button was clicked most recently
    # if int(btn_add) > int(btn_remove):
       
        # edges.append({'data': {
        #                         'id': "edge" + str(edgeId), 
        #                         'source':str(sourceid), 
        #                         'target':str(targetid),
        #                         'label': 'edge ' + str(sourceid) + str(targetid) 
        #                         }
        #                     })
    #     return nodes + edges

    # # If the remove button was clicked most recently
    # elif int(btn_remove) > int(btn_add):
            # nodes = [x for x in edges if not x['data']['id'] == edgeId]
    #         return nodes + edges

#     # Neither have been clicked yet (or fallback condition)
#     return elements

if __name__ == '__main__':
    app.run_server(debug=True)