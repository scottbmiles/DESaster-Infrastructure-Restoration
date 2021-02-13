__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import random
import numpy as np
import math


def modified_base_pga_random(pga):

    dist = [0.2, 0.3, 0.3, 0.2] # probability of locating an entity of soil type A, B, C and D
    amp_f = [0.8, 1, 1.1, 1.3]  # amplification factor to amplify pga_b according to its site
    return pga*np.random.choice(amp_f, 1, p=dist).tolist()[0]


def seismic_hazard_evaluation_random(F, pga_b):

    for n in F.nodes():
        F.nodes[n]['pga'] = modified_base_pga_random(pga_b)

    for u,v in F.edges():
        F[u][v][0]['pga'] = modified_base_pga_random(pga_b)
        if F[u][v][0]['direct'] == 2:
            F[v][u][0]['pga'] = F[u][v][0]['pga']

    return F


def main():

    #TODO: Parsing
    G = seismic_hazard_evaluation_random(G, base_pga)

    return G


if __name__ == '__main__':

    main()