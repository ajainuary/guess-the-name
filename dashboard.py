import json

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import dash_cytoscape as cyto

app = dash.Dash(__name__)
server = app.server

# Object declaration
basic_elements = []

G=nx.Graph()
G.add_nodes_from(["a","b","c","d",1,2])
G.add_edges_from([("a","c"),("c","d"), ("a",1), (1,"d"), ("a",2)])
pos = nx.layout.spring_layout(G)

for node in G.nodes:
    G.nodes[node]['pos'] = list(pos[node])

for node in G.nodes():
    basic_elements.append({'data': {
                                'id': str(node), 
                                'label': 'Node ' + str(node),
                                'visible': False
                                }, 
                            'position': {
                                'x': G.nodes[node]['pos'][0], 
                                'y': G.nodes[node]['pos'][1]
                                }
                        })

index = 0
for edge in G.edges():
    basic_elements.append({'data': {
                                'id': "edge" + str(index), 
                                'source':str(edge[0]), 
                                'target':str(edge[1]),
                                'label': 'edge ' + str(edge[0]) + str(edge[1]) 
                                }
                            })
    index += 1

styles = {
    'json-output': {
        'overflow-y': 'scroll',
        'height': 'calc(50% - 25px)',
        'border': 'thin lightgrey solid'
    },
    'tab': {'height': 'calc(98vh - 115px)'}
}

app.layout = html.Div([
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=basic_elements,
            style={
                'height': '500px',
                'width': '500px'
            }
        )
    ]),

    html.Div(className='one columns', children=[
            dcc.Dropdown(
                id='NodeList',
                options=[
                    {'label': 'New York City', 'value': 'NYC'},
                    {'label': 'Montreal', 'value': 'MTL'},
                    {'label': 'San Francisco', 'value': 'SF'}
                ],
                value='NYC',
                multi=False,
                placeholder="Select a node"
        )]),

    html.Div([
    html.Button('Add Node', id='btn-add-node', n_clicks_timestamp=0),
    html.Button('Remove Node', id='btn-remove-node', n_clicks_timestamp=0)
        ]),


    # html.Div(className='four columns', children=[
    #     dcc.Tabs(id='tabs', children=[
    #         dcc.Tab(label='Tap Objects', children=[
    #             html.Div(style=styles['tab'], children=[
    #                 html.P('Node Object JSON:'),
    #                 html.Pre(
    #                     id='tap-node-json-output',
    #                     style=styles['json-output']
    #                 ),
    #                 html.P('Edge Object JSON:'),
    #                 html.Pre(
    #                     id='tap-edge-json-output',
    #                     style=styles['json-output']
    #                 )
    #             ])
    #         ]),

    #         dcc.Tab(label='Tap Data', children=[
    #             html.Div(style=styles['tab'], children=[
    #                 html.P('Node Data JSON:'),
    #                 html.Pre(
    #                     id='tap-node-data-json-output',
    #                     style=styles['json-output']
    #                 ),
    #                 html.P('Edge Data JSON:'),
    #                 html.Pre(
    #                     id='tap-edge-data-json-output',
    #                     style=styles['json-output']
    #                 )
    #             ])
    #         ]),

    #         dcc.Tab(label='Mouseover Data', children=[
    #             html.Div(style=styles['tab'], children=[
    #                 html.P('Node Data JSON:'),
    #                 html.Pre(
    #                     id='mouseover-node-data-json-output',
    #                     style=styles['json-output']
    #                 ),
    #                 html.P('Edge Data JSON:'),
    #                 html.Pre(
    #                     id='mouseover-edge-data-json-output',
    #                     style=styles['json-output']
    #                 )
    #             ])
    #         ]),
    #         dcc.Tab(label='Selected Data', children=[
    #             html.Div(style=styles['tab'], children=[
    #                 html.P('Node Data JSON:'),
    #                 html.Pre(
    #                     id='selected-node-data-json-output',
    #                     style=styles['json-output']
    #                 ),
    #                 html.P('Edge Data JSON:'),
    #                 html.Pre(
    #                     id='selected-edge-data-json-output',
    #                     style=styles['json-output']
    #                 )
    #             ])
    #         ])
    #     ]),
    # ]),

    html.Div(id='placeholder')
])

@app.callback(Output('cytoscape', 'elements'),
              [Input('btn-add-node', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              Input('NodeList', 'value'),
              State('cytoscape', 'elements')])
def update_elements(btn_add, btn_remove, nodeId, elements):
    # If the add button was clicked most recently
    if int(btn_add) > int(btn_remove):
        # As long as we have not reached the max number of nodes, we add them
        # to the cytoscape elements
        return elements + [{'data': {
                                'id': str(nodeId), 
                                'label': 'Node ' + str(nodeId)
                                } 
                            # 'position': {
                            #     'x': G.nodes[node]['pos'][0], 
                            #     'y': G.nodes[node]['pos'][1]
                            #     }
                        }]

    # If the remove button was clicked most recently
    elif int(btn_remove) > int(btn_add):
            return elements[:-1]

    # Neither have been clicked yet (or fallback condition)
    return elements


# @app.callback(Output('tap-node-json-output', 'children'),
#               [Input('cytoscape', 'tapNode')])
# def displayTapNode(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('tap-edge-json-output', 'children'),
#               [Input('cytoscape', 'tapEdge')])
# def displayTapEdge(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('tap-node-data-json-output', 'children'),
#               [Input('cytoscape', 'tapNodeData')])
# def displayTapNodeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('tap-edge-data-json-output', 'children'),
#               [Input('cytoscape', 'tapEdgeData')])
# def displayTapEdgeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('mouseover-node-data-json-output', 'children'),
#               [Input('cytoscape', 'mouseoverNodeData')])
# def displayMouseoverNodeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('mouseover-edge-data-json-output', 'children'),
#               [Input('cytoscape', 'mouseoverEdgeData')])
# def displayMouseoverEdgeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('selected-node-data-json-output', 'children'),
#               [Input('cytoscape', 'selectedNodeData')])
# def displaySelectedNodeData(data):
#     return json.dumps(data, indent=2)


# @app.callback(Output('selected-edge-data-json-output', 'children'),
#               [Input('cytoscape', 'selectedEdgeData')])
# def displaySelectedEdgeData(data):
#     return json.dumps(data, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)