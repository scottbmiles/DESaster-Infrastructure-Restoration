__version__ = "0.5"
__status__ = "In progress"

"""
This script is used to get data for an infrastructure network system. The input data include
information about nodes and edges.
"""

import networkx as nx
import argparse


def get_nodes(nd_dir, nw_n):

    nodes_in = {}
    try:
        with open(nd_dir, 'r') as nd_f:

            next(nd_f)
            for row in nd_f:

                row = row.split(',')
                nodes_in[row[0]] = {
                    'id': row[0],
                    'type': row[1],
                    'loc': (float(row[2]), float(row[3])),
                    'reqExpr_Mean': int(row[4]),
                    'reqExpr_SD': int(row[5]),
                    'reqExpr_Dist': row[6],
                    'reqTime_Mean': int(row[7]),
                    'reqTime_SD': int(row[8]),
                    'reqTime_Dist': row[9],
                    'reqBudg_Mean': int(row[10]),
                    'reqBudg_SD': int(row[11]),
                    'reqBudg_Dist': row[12],
                    'reqEqp': row[13],
                    'priority': int(row[14]),
                    'dmgProb': float(row[15]),
                    'dep_Mean': float(row[16]),
                    'dep_SD': float(row[17]),
                    'dep_Dist': row[18],
                    'exist': True,
                    'status': 'operational',
                    'infr': nw_n
                }
    except FileNotFoundError as error:
        print(error)
    return nodes_in


def get_edges(ed_dir, nw_n):
    edges_in = {}

    try:
        with open(ed_dir, 'r') as ed_f:

            next(ed_f)
            for row in ed_f:
                row = row.split(',')
                # TODO: Mybe adding TRY/Exception
                edges_in[row[0]] = {
                    'id' : row[0],
                    'nodes': (row[1], row[2]),
                    'type': row[3],
                    'direct': int(row[4]),
                    'reqExpr_Mean': int(row[5]),
                    'reqExpr_SD': int(row[6]),
                    'reqExpr_Dist': row[7],
                    'reqTime_Mean': int(row[8]),
                    'reqTime_SD': int(row[9]),
                    'reqTime_Dist': row[10],
                    'reqBudg_Mean': float(row[11]),
                    'reqBudg_SD': float(row[12]),
                    'reqBudg_Dist' : row[13],
                    'reqEqp': row[14],
                    'dmgProb': float(row[15]),
                    'dep_Mean': float(row[16]),
                    'dep_SD': float(row[17]),
                    'dep_Dist': row[18],
                    'status': 'operational',
                    'infr': nw_n
                }
    except FileNotFoundError as error:
        print(error)

    return edges_in


def _parse_data():
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
    parser.add_argument('-w',
                        '--network_system',
                        type=str,
                        required=True,
                        help='insert the name of network system (e.g. Electric, or Water)')

    args = parser.parse_args()
    return args.nodes, args.edges, args.network_system


def main():

    node_dir, edge_dir, nw_name = _parse_data()
    nodes = get_nodes(node_dir, nw_name)
    edges = get_edges(edge_dir, nw_name)

    return nodes, edges


if __name__ == "__main__":

    main()
