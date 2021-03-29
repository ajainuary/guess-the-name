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
nodes = []
edges = []

G=nx.Graph()
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
    html.Div(className='eight columns', children=[
        cyto.Cytoscape(
            id='cytoscape',
            elements=basic_elements,
            stylesheet=graph_stylesheet,
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
    html.Div(id='placeholder')
])

@app.callback(Output('cytoscape', 'elements'),
              [Input('btn-add-node', 'n_clicks_timestamp'),
              Input('btn-remove-node', 'n_clicks_timestamp'),
              State('NodeList', 'value'),
              State('cytoscape', 'elements')])
def add_delete_node(btn_add, btn_remove, nodeId, elements):
    global nodes
    global edges
    # If the add button was clicked most recently
    if int(btn_add) > int(btn_remove):
        nodes.append({'data': {
                                'id': str(nodeId), 
                                'label': 'Node ' + str(nodeId)
                                } 
                    })
        return nodes + edges

    # If the remove button was clicked most recently
    elif int(btn_remove) > int(btn_add):
            nodes = [x for x in nodes if not x['data']['id'] == nodeId]
            return nodes + edges

    # Neither have been clicked yet (or fallback condition)
    return elements

if __name__ == '__main__':
    app.run_server(debug=True)