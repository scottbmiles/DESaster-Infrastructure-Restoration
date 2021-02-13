__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse

def gen_graph(node_list, edge_list, graph_type=4):

    if graph_type == 1:
        G = nx.Graph()
    elif graph_type == 2:
        G = nx.DiGraph()
    elif graph_type == 3:
        G = nx.MultiGraph()
    elif graph_type == 4:
        G = nx.MultiDiGraph()
    else:
        print(
            "This type of graph is not defined! Select from options (1 to 4).\n"
            "MultiDiGraph is selected as a default. If not appropriate, run the script again."
        )
        G = nx.MultiDiGraph()

    for node in node_list:
        G.add_node(node,
                   type=node_list[node]['type'],
                   pos=node_list[node]['loc'],
                   infr=node_list[node]['infr'])

    for edge in edge_list:
        G.add_edge(
            edge_list[edge]['nodes'][0],
            edge_list[edge]['nodes'][1],
            edge_list[edge]['infr'][2]
        )
        if edge_list[edge]['direct'] == 2:
            G.add_edge(
                edge_list[edge]['nodes'][1],
                edge_list[edge]['nodes'][0],
                edge_list[edge]['infr'][2]
            )
    # pos = nx.get_node_attributes(G, 'pos')
    return G

def parsing():

    parser = argparse.ArgumentParser(
        description='This function is used to get coordinates of nodes '
        'and edges and their conductivities. You need to '
        'insert nodes and edges as two files.',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-n',
                        '--nodes',
                        type=str,
                        required=True,
                        help='insert path of node file')
    parser.add_argument(
        '-e',
        '--edges',
        type=str,
        required=True,
        help='insert path of edge file (connections between nodes)')

    parser.add_argument('-g',
                        '--graph',
                        default=4,
                        type=int,
                        help='select graph type (optional): \n'
                        '1: undirected simple graph (Graph)\n'
                        '2: directed simple graph (DiGraph)\n'
                        '3: undirected graph with parallel loop (MultiGraph)\n'
                        '4 (default): directed graph with parallel loop')

    args = parser.parse_args()
    return args.nodes, args.edges, args.network_system, args.graph

def main():

    [nodes, edges, ntw_name, graph_type] = parsing()
    G = gen_graph(nodes, edges, graph_type)
    return G

if __name__ == '__main__':

    main()