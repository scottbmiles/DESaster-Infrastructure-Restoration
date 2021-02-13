__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import random
import numpy as np
import math


def required_resources_for_repair_norm_dist(G):

    # cost damage ration based on level of damage:
    cost_damage = {
        'slight': 0.0,  # these ratios are default values proposed in Hazus
        'moderate': 0.1,
        'extensive': 0.5,
        'complete': 1.0
        }

    # using normal distribution to estimate required resources
    # inserted resources are considered as mean and we assume that
    # standard deviation is 20% of the mean
    # TODO: ask mean and sd from users to provide ...

    for n in G.nodes():

        G.nodes[n]['reqTime'] = int(np.random.normal(G.nodes[n]['reqTime'], 0.2*G.nodes[n]['reqTime']))
        G.nodes[n]['reqBudg'] = int(np.random.normal(G.nodes[n]['reqBudg'], 0.2*G.nodes[n]['reqBudg']))
        G.nodes[n]['reqExpr'] = int(np.random.normal(G.nodes[n]['reqExpr'], 0.2*G.nodes[n]['reqExpr']))
        # G.nodes[n]['status'] = 'damaged'
        # if G.nodes[n]['dmg_state'] == 'slight':
        #     G.nodes[n]['status'] = 'inoperational'
        #     G.nodes[n]['reqEqp'] = 'NA'

    for u,v in G.edges():

        G[u][v][0]['reqTime'] = int(np.random.normal(G[u][v][0]['reqTime'], 0.2*G[u][v][0]['reqTime']))
        G[u][v][0]['reqBudg'] = int(np.random.normal(G[u][v][0]['reqBudg'], 0.2*G[u][v][0]['reqBudg']))
        G[u][v][0]['reqExpr'] = int(np.random.normal(G[u][v][0]['reqExpr'], 0.2*G[u][v][0]['reqExpr']))
        # G[u][v][0]['status'] = 'damaged'
        # if G[u][v][0]['dmg_state'] == 'slight':
        #     G[u][v][0]['reqEqp'] = 'NA'
        #     G[u][v][0]['status'] = 'inoperational'

    # required resources are determined based on damage state suggested by HAZUS

    for n in G.nodes():

        G.nodes[n]['reqTime'] *= cost_damage[G.nodes[n]['dmg_state']]
        G.nodes[n]['reqBudg'] *= cost_damage[G.nodes[n]['dmg_state']]
        G.nodes[n]['reqExpr'] *= cost_damage[G.nodes[n]['dmg_state']]
        # G.nodes[n]['status'] = 'damaged'
        # if G.nodes[n]['dmg_state'] == 'slight':
        #     G.nodes[n]['status'] = 'inoperational'
        #     G.nodes[n]['reqEqp'] = 'NA'

    for u,v in G.edges():

        G[u][v][0]['reqTime'] *= cost_damage[G[u][v][0]['dmg_state']]
        G[u][v][0]['reqBudg'] *= cost_damage[G[u][v][0]['dmg_state']]
        G[u][v][0]['reqExpr'] *= cost_damage[G[u][v][0]['dmg_state']]
        # G[u][v][0]['status'] = 'damaged'
        # if G[u][v][0]['dmg_state'] == 'slight':
        #     G[u][v][0]['reqEqp'] = 'NA'
        #     G[u][v][0]['status'] = 'inoperational'

    return G


def main():

    #TODO: Parsing
    G = required_resources_for_repair_norm_dist(G)

    return G


if __name__ == '__main__':

    main()