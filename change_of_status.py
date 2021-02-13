__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import simpy
import json
import viz
import numpy as np
import random


def entity_change_of_status(G, ent, new_status, time):

    if ent in G.nodes():
        G.nodes[ent]['status'] = new_status
        G.nodes[ent]['output'][new_status] = time

    else:
        G[ent[0]][ent[1]][0]['status'] = new_status
        G[ent[0]][ent[1]][0]['output'][new_status] = time

        if G[ent[0]][ent[1]][0]['direct'] == 2:
            G[ent[1]][ent[0]][0]['status'] = new_status
            G[ent[1]][ent[0]][0]['output'][new_status] = time
    # viz.display_graph(G, 'save', time)


def check_operationality_from_source(G, src, time, prev_nodes=None):

    if prev_nodes is None:
        prev_nodes = []

    acp_status = ['functional', 'operational']
    neighbors = G.neighbors(src)
    for n in neighbors:
        if n in prev_nodes:
            continue
        else:
            prev_nodes.append(n)

        if G.nodes[n]['status'] in acp_status and G[src][n][0]['status'] in acp_status and G.nodes[n]['dep'] <= time:
            G.nodes[n]['status'] = G[src][n][0]['status'] = 'operational'
            if G.nodes[n]['output']['operational'] < 0:
                G.nodes[n]['output']['operational'] = time
            if G[src][n][0]['output']['operational'] < 0:
                G[src][n][0]['output']['operational'] = time
                if G[src][n][0]['direct'] == 2:
                    G[n][src][0]['status'] = G[src][n][0]['status']
                    G[n][src][0]['output']['operational'] = G[src][n][0]['output']['operational']

            check_operationality_from_source(G, n, time, prev_nodes)


def change_of_status_based_on_source(G, time):

    sources = [n for n in G.nodes() if G.nodes[n]['type'] == 'source']
    for s in sources:
        check_operationality_from_source(G, s, time)
    # viz.display_graph(G, 'save', time)


def change_of_status_shortest_path(G, t):

    sources = [k for k in G.nodes() if G.nodes[k]['type'] == 'source']
    other_nodes = [k for k in G.nodes() if G.nodes[k]['type'] != 'source']

    for node in other_nodes:
        for src in sources:
            if nx.has_path(G, src, node) is False:
                continue
            shortest_path = nx.shortest_path(G, src, node, weight='reqTime')
            if nx.dijkstra_path_length(G, source=src, target=node, weight='reqTime') == 0:
                for n in shortest_path:
                    entity_change_of_status(G, n, 'operational', t)
                for u,v in zip(shortest_path[:1], shortest_path[1:]):
                    entity_change_of_status(G, (u,v), 'operational', t)


def change_based_of_neighbor(G, node, t):

    neighbors = list(G.neighbors(node))

    for n in neighbors:

        if G[node][n][0]['status'] == 'functional' or 'operational':
            entity_change_of_status(G, (node, n), 'operational', t)

            if G.nodes[n]['status'] == 'functional' or 'operational':
                entity_change_of_status(G, n, 'operational',t )
                return change_based_of_neighbor(G, n, t)

        else:
            pass


def main():

    # # TODO: Parsing
    # # TODO: Monitoring

    return


if __name__ == '__main__':

    main()
