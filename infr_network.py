__version__ = "0.5"
__status__ = "In progress"


import argparse
import networkx as nx
import matplotlib.pyplot as plt



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

        G.add_node(
            node,
            id=node_list[node]['id'],
            pos=node_list[node]['loc'],
            type=node_list[node]['type'],
            infr=node_list[node]['infr'],
            reqExpr = node_list[node]['reqExpr_Mean'],
            reqExprM = node_list[node]['reqExpr_Mean'],
            reqExprSD = node_list[node]['reqExpr_SD'],
            reqExprD = node_list[node]['reqExpr_Dist'],
            reqTime = node_list[node]['reqTime_Mean'],
            reqTimeM = node_list[node]['reqTime_Mean'],
            reqTimeSD = node_list[node]['reqTime_SD'],
            reqTimeD = node_list[node]['reqTime_Dist'],
            reqBudg = node_list[node]['reqBudg_Mean'],
            reqBudgM = node_list[node]['reqBudg_Mean'],
            reqBudgSD = node_list[node]['reqBudg_SD'],
            reqBudgD = node_list[node]['reqBudg_Dist'],
            reqEqp = node_list[node]['reqEqp'],
            dep = node_list[node]['dep_Mean'],
            depSD = node_list[node]['dep_SD'],
            depD = node_list[node]['dep_Dist'],
            status = node_list[node]['status'],
            output = {'pre': -1, 'damaged': 0, 'processing':0, 'functional': 0, 'operational': -1},
            pri = node_list[node]['priority'],
            dmgProb=node_list[node]['dmgProb']
        )

    for edge in edge_list:

        G.add_edge(
            edge_list[edge]['nodes'][0],
            edge_list[edge]['nodes'][1],
            id=edge_list[edge]['id'],
            type=edge_list[edge]['type'],
            infr=edge_list[edge]['infr'],
            direct=edge_list[edge]['direct'],
            reqExpr = edge_list[edge]['reqExpr_Mean'],
            reqExprM = edge_list[edge]['reqExpr_Mean'],
            reqExprSD = edge_list[edge]['reqExpr_SD'],
            reqExprD = edge_list[edge]['reqExpr_Dist'],
            reqTime = edge_list[edge]['reqTime_Mean'],
            reqTimeM = edge_list[edge]['reqTime_Mean'],
            reqTimeSD = edge_list[edge]['reqTime_SD'],
            reqTimeD = edge_list[edge]['reqTime_Dist'],
            reqBudg = edge_list[edge]['reqBudg_Mean'],
            reqBudgM = edge_list[edge]['reqBudg_Mean'],
            reqBudgSD = edge_list[edge]['reqBudg_SD'],
            reqBudgD = edge_list[edge]['reqBudg_Dist'],
            reqEqp = edge_list[edge]['reqEqp'],
            dep = edge_list[edge]['dep_Mean'],
            depSD = edge_list[edge]['dep_SD'],
            depD = edge_list[edge]['dep_Dist'],
            status = edge_list[edge]['status'],
            output = {'pre': -1, 'damaged': 0, 'processing':0, 'functional': 0, 'operational': -1},
            dmgProb= edge_list[edge]['dmgProb']
        )
        if edge_list[edge]['direct'] == 2:
            G.add_edge(
                edge_list[edge]['nodes'][1],
                edge_list[edge]['nodes'][0],
                id=edge_list[edge]['id'],
                type=edge_list[edge]['type'],
                infr=edge_list[edge]['infr'],
                direct=edge_list[edge]['direct'],
                reqExpr = edge_list[edge]['reqExpr_Mean'],
                reqExprM = edge_list[edge]['reqExpr_Mean'],
                reqExprSD = edge_list[edge]['reqExpr_SD'],
                reqExprD = edge_list[edge]['reqExpr_Dist'],
                reqTime = edge_list[edge]['reqTime_Mean'],
                reqTimeM = edge_list[edge]['reqTime_Mean'],
                reqTimeSD = edge_list[edge]['reqTime_SD'],
                reqTimeD = edge_list[edge]['reqTime_Dist'],
                reqBudg = edge_list[edge]['reqBudg_Mean'],
                reqBudgM = edge_list[edge]['reqBudg_Mean'],
                reqBudgSD = edge_list[edge]['reqBudg_SD'],
                reqBudgD = edge_list[edge]['reqBudg_Dist'],
                reqEqp = edge_list[edge]['reqEqp'],
                status = edge_list[edge]['status'],
                output = {'pre': -1, 'damaged': 0, 'processing':0, 'functional': 0, 'operational': -1},
                dmgProb= edge_list[edge]['dmgProb']
            )

    return G


def combine_graphs(G, H):

    return nx.compose(G,H)


def parsing():

    parser = argparse.ArgumentParser(
        description='This function is used to get coordinates of nodes '
        'and edges and their conductivities. You need to '
        'insert nodes and edges as two files.',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '-n',
        '--nodes',
        type=str,
        required=True,
        help='insert node data'
    )

    parser.add_argument(
        '-e',
        '--edges',
        type=str,
        required=True,
        help='insert edge data (connections between nodes)'
    )

    parser.add_argument(
        '-g',
        '--graph',
        default=4,
        type=int,
        help='select graph type (optional): \n'
        '1: undirected simple graph (Graph)\n'
        '2: directed simple graph (DiGraph)\n'
        '3: undirected graph with parallel loop (MultiGraph)\n'
        '4 (default): directed graph with parallel loop'
    )

    args = parser.parse_args()

    return args.nodes, args.edges, args.network_system, args.graph


def main():

    nodes, edges, ntw_name, graph_type = parsing()
    G = gen_graph(nodes, edges, graph_type)
    # G = combine_graphs(G, H)
    return G

if __name__ == '__main__':

    main()