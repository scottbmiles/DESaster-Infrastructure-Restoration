__version__ = "0.5"
__status__ = "In progress"

"""
This script is used to get data for an infrastructure network system. The input data include
information about nodes and edges.
"""

import networkx as nx
import argparse
import random
import numpy as np
import math
import change_of_status as cos


def damage_state_random(G, haz_int):

    # TODO: chance of damage for each entity could be different
    dmg_prb = 0.45 if haz_int == 'strong' else 0.25 if haz_int == 'medium' else 0.1

    for node in G.nodes():
        if random.random() > dmg_prb: # randomly detected as damaged entity
            G.nodes[node]['reqTime'] = 0
            G.nodes[node]['reqBudg'] = 0
            G.nodes[node]['reqExpr'] = 0
            G.nodes[node]['reqEqp'] = 'NA'
            G.nodes[node]['status'] = 'inoperative'
        else:
            G.nodes[node]['status'] = 'damaged'

    for (u, v) in G.edges():
        #TODO: think about how to make sure that dmg_prb for bi-directional edges is correct
        if random.random() > dmg_prb: # randomly detected as damaged entity
            G[u][v][0]['reqTime'] = 0
            G[u][v][0]['reqBudg'] = 0
            G[u][v][0]['reqExpr'] = 0
            G[u][v][0]['reqEqp'] = 'NA'
            G[u][v][0]['status'] = 'inoperative'
        else:
            G[u][v][0]['status'] = 'damaged'

    # # unifying damage status for bidirectional edges:
    for (u, v) in G.edges():
        if G[u][v][0]['direct'] == 2 and G[u][v][0]['status'] != G[v][u][0]['status']:
            if random.random() > 0.5:
                G[v][u][0]['status'] = G[u][v][0]['status']
                G[v][u][0]['reqTime'] = G[u][v][0]['reqTime']
                G[v][u][0]['reqBudg'] = G[u][v][0]['reqBudg']
                G[v][u][0]['reqExpr'] = G[u][v][0]['reqExpr']
                G[v][u][0]['reqEqp'] = G[u][v][0]['reqEqp']
            else:
                G[u][v][0]['status'] = G[v][u][0]['status']
                G[u][v][0]['reqTime'] = G[v][u][0]['reqTime']
                G[u][v][0]['reqBudg'] = G[v][u][0]['reqBudg']
                G[u][v][0]['reqExpr'] = G[v][u][0]['reqExpr']
                G[u][v][0]['reqEqp'] = G[v][u][0]['reqEqp']
        else:
            pass

    print(len([n for n in G.nodes() if G.nodes[n]['status']=='damaged']) +
          len([u for u,v in G.edges() if G[u][v][0]['status']=='damaged']))
    return G

def _damage_prob_random_in_range(mu, s, min, max):

    p = 0
    while not min < p <= max:
        p = np.random.normal(mu, s)
    return p


def damage_state_per_entity(pga, rp):

    # TODO: Find these factors for entities from codes published by Homeland Security ...
    # probability of occurring damage in different state:
    # damage states are ['slight', 'moderate', 'extensive', 'complete'] respectively
    mu_s, mu_m, mu_e, mu_c, sigma_s, sigma_m, sigma_e, sigma_c = 0, 0, 0, 0, 0, 0, 0, 0
    s_min, m_min, e_min, c_min = 0, 0, 0, 0

    if rp == 475:
        mu_s, sigma_s = 0.95, 0.03 # mean and standard deviation for slight damage state
        mu_m, sigma_m = 0.6, 0.1 # moderate state
        mu_e, sigma_e = 0.4, 0.1 # extensive state
        mu_c, sigma_c = 0.2, 0.1 # complete damage
        s_min = 0.5  #  minimum acceptable range for slight damage state
        m_min = 0.3  #  moderate
        e_min = 0.1  #  extensive
        c_min = 0.0  #  complete

    elif rp == 2475:
        mu_s, sigma_s = 0.99, 0.1 # mean and standard deviation
        mu_m, sigma_m = 0.85, 0.1 # moderate state
        mu_e, sigma_e = 0.65, 0.1 # extensive state
        mu_c, sigma_c = 0.35, 0.1 # complete damage
        s_min = 0.95  # acceptable range for slight damage state
        m_min = 0.7
        e_min = 0.4
        c_min = 0.2
    else:
        print('error: this return period is not defined ... ')
        exit()

    weight = [0]*4
    weight[0] = _damage_prob_random_in_range(mu_s, sigma_s, s_min, 1.0)
    weight[1] = _damage_prob_random_in_range(mu_m, sigma_m, m_min, 0.85 * weight[0])
    weight[2] = _damage_prob_random_in_range(mu_e, sigma_e, e_min, 0.9 * weight[1])
    weight[3] = _damage_prob_random_in_range(mu_c, sigma_c, c_min, 0.9 * weight[2])

    # normalize weights
    weight = [w/sum(weight[:]) for w in weight]

    return np.random.choice(['slight', 'moderate', 'extensive', 'complete'], 1, p=weight).tolist()[0]


def damage_state_user_defined_fragility(F, return_period):

    # here we randomly select median capacity (mu) and standard deviation (beta)
    for n in F.nodes():
        pga = F.nodes[n]['pga']
        F.nodes[n]['dmg_state'] = damage_state_per_entity(pga, return_period)
        F.nodes[n]['status'] = 'inoperative' if F.nodes[n]['dmg_state'] == 'slight' else 'damaged'

    for u,v in F.edges():
        pga = F[u][v][0]['pga']
        F[u][v][0]['dmg_state'] = damage_state_per_entity(pga, return_period)
        F[u][v][0]['status'] = 'inoperative' if F[u][v][0]['dmg_state'] == 'slight' else 'damaged'
        if F[u][v][0]['direct'] == 2:
            F[v][u][0]['dmg_state'] = F[u][v][0]['dmg_state']
            F[v][u][0]['status'] = F[u][v][0]['status']

    return F


def deteremine_req_resources(method, mu, sigma):

    if method == 'uniform':
        return mu
    elif method == 'normDist':
        return max(int(random.normalvariate(mu, sigma)), 1)
    elif method == 'logNormDist':
        return max(int(random.lognormvariate(mu, sigma)), 1)
    else:
        print(method)
        raise ValueError("the inserted reqRes is invalid! It should be 'mean', 'normDist', or 'logNormDist'")

def user_defined_damage_state(G):

    """

    """

    for n in G.nodes():

        if G.nodes[n]['type'] == 'source':
            continue

        dmg = 1 if random.random() < G.nodes[n]['dmgProb'] else 0

        if dmg == 1:
            G.nodes[n]['status'] = 'damaged'
            G.nodes[n]['output']['damaged'] = 0
            G.nodes[n]['reqTime'] = deteremine_req_resources(G.nodes[n]['reqTimeD'], G.nodes[n]['reqTimeM'], G.nodes[n]['reqTimeSD'])
            G.nodes[n]['reqExpr'] = deteremine_req_resources(G.nodes[n]['reqExprD'], G.nodes[n]['reqExprM'], G.nodes[n]['reqExprSD'])
            G.nodes[n]['reqBudg'] = deteremine_req_resources(G.nodes[n]['reqBudgD'], G.nodes[n]['reqBudgM'], G.nodes[n]['reqBudgSD'])

        elif G.nodes[n]['type'] == 'source':
            G.nodes[n]['status'] = 'operational'
            G.nodes[n]['output']['operational'] = 0
        else:
            G.nodes[n]['reqTime'] = 0
            G.nodes[n]['reqExpr'] = 0
            G.nodes[n]['reqBudg'] = 'NA'
            G.nodes[n]['status'] = 'functional'
            G.nodes[n]['output']['functional'] = 0

    prev = []
    for u,v in G.edges():
        if (v, u) not in prev:
            prev.append((u,v))
            dmg = 1 if random.random() < G[u][v][0]['dmgProb'] else 0
            if dmg == 1:
                G[u][v][0]['status'] = 'damaged'
                G[u][v][0]['output']['damaged'] = 0
                G[u][v][0]['reqTime'] = deteremine_req_resources(G[u][v][0]['reqTimeD'], G[u][v][0]['reqTimeM'], G[u][v][0]['reqTimeSD'])
                G[u][v][0]['reqExpr'] = deteremine_req_resources(G[u][v][0]['reqExprD'], G[u][v][0]['reqExprM'], G[u][v][0]['reqExprSD'])
                G[u][v][0]['reqBudg'] = deteremine_req_resources(G[u][v][0]['reqBudgD'], G[u][v][0]['reqBudgM'], G[u][v][0]['reqBudgSD'])

            else:
                G[u][v][0]['reqTime'] = 0
                G[u][v][0]['reqExpr'] = 0
                G[u][v][0]['reqBudg'] = 0
                G[u][v][0]['status'] = 'functional'
                G[u][v][0]['output']['functional'] = 0

            if G[u][v][0]['direct'] == 2:
                G[v][u][0]['reqTime'] = G[u][v][0]['reqTime']
                G[v][u][0]['reqExpr'] = G[u][v][0]['reqExpr']
                G[v][u][0]['reqBudg'] = G[u][v][0]['reqBudg']
                G[v][u][0]['status']  = G[u][v][0]['status']
                G[v][u][0]['output'] = G[u][v][0]['output']

    cos.change_of_status_based_on_source(G, 0)

    return G


def probabilistic_damage_state_user_defined_fragility_curves(G):

    # Implement this function for more challenging scenarios ...

    print('not defined yet!')


def main():

    #TODO: Parsing
    G = damage_state_user_defined_fragility(G, rp)
    G = user_defined_damage_state(G)
    G = probabilistic_damage_state_user_defined_fragility_curves(G)

    return G


if __name__ == '__main__':

    main()