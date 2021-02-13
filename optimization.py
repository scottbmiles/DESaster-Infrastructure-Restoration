__version__ = "0.5"
__status__ = "In progress"


import argparse
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import copy
import monitoring


def _distribute_node_weight(F, arg):

    # TODO: investigate this time carefully with different examples to make sure it works correctly
    for (u, v) in F.edges():

        # number of neighbors of u and v
        n_nbr_u = len(list(F.neighbors(u)))
        n_nbr_v = len(list(F.neighbors(v)))

        # distributed portion of nodes on edge
        nA_w = F.nodes[u][arg] if n_nbr_u < 2 else F.nodes[u][arg]/2
        nB_w = F.nodes[v][arg] if n_nbr_v < 2 else F.nodes[v][arg]/2
        F[u][v][0]['weight'] = F[u][v][0][arg] + nA_w + nB_w

    return


def cust_rec_time(F, arg, cust, src):
    """
    This function returns minimum required time to recover customer
    """
    _distribute_node_weight(F, arg)
    return min([nx.dijkstra_path_length(F, source=source, target=cust) for source in src if nx.has_path(F, source, cust)])


def critical_entity(F, src, trg, method, arg, n_param, av_ex, av_bg):

    # minimum required time to recover selected customers
    recTime_t0 = np.array([cust_rec_time(F, arg, cust, src) for cust in trg])

    reduced_rec_time = {}
    for n in F.nodes():
        n_t = F.node[n]['reqTime']
        if n_t > 0:# and F.node[n]['reqBudg'] < av_bg and F.node[n]['reqBudg'] < av_ex:
            # print([F.nodes[m]['reqTime'] for m in F.nodes()])
            F.nodes[n]['reqTime'] = 0
            # minimum require time to recover customers after fixing a damaged node
            recTime_t1 = np.array([cust_rec_time(F, arg, cust, src) for cust in trg])
            reduced_rec_time[n] = sum(recTime_t0 - recTime_t1)#/F.nodes[n][n_param]
            F.nodes[n]['reqTime'] = n_t

    # print([F.nodes[node]['reqTime'] for node in F.nodes()])
    for (u, v) in F.edges():
        e_t = F[u][v][0]['reqTime']
        if e_t > 0: #and F[u][v][0]['reqBudg'] < av_bg and F[u][v][0]['reqBudg'] < av_ex:
            F[u][v][0]['reqTime'] = 0
            if F[u][v][0]['direct'] == 2: F[v][u][0]['reqTime'] = 0
            # minimum require time to recover customers after fixing a damaged edge
            recTime_t1 = np.array([cust_rec_time(F, arg, cust, src) for cust in trg])
            reduced_rec_time[(u, v)] = sum(recTime_t0 - recTime_t1)#/F[u][v][0][n_param]
            F[u][v][0]['reqTime'] = e_t
            if F[u][v][0]['direct'] == 2: F[v][u][0]['reqTime'] = e_t

    try:
        crt_ent = max(reduced_rec_time, key=reduced_rec_time.get)
    except:
        crt_ent = list(reduced_rec_time.keys())[0]
    # print('recovery of {} is the most influential damaged entity.\n'
    #       'Getting this entity recovered will reduce the recovery process'
    #       ' by {} days'.format(crt_ent, reduced_rec_time[crt_ent]))
    return crt_ent


def optimized_list_of_entites(F, sources, trg_p1, method, opt_param, norm_param, av_expr, av_budg):

    G = copy.deepcopy(F)
    rec_ent_list = []
    # crt_ent = critical_entity(G, sources, targets, method, opt_param, norm_param, av_exprts)
    n_damaged = sum(1 for ent in F.nodes() if F.nodes[ent]['reqTime']>0)+\
                sum(1 for (u,v) in F.edges() if F[u][v][0]['reqTime']>0 and F[u][v][0]['direct']==1)+\
                sum(1 for (u,v) in F.edges() if F[u][v][0]['reqTime']>0 and F[u][v][0]['direct']==2)/2

    print('number of damaged entities:',n_damaged)
    for i in range(int(n_damaged)):
        ent = critical_entity(G, sources, trg_p1, method, opt_param, norm_param, av_expr, av_budg)
        rec_ent_list.append(ent)
        if ent in G.nodes():
            G.nodes[ent]['reqTime'] = 0
        else:
            G[ent[0]][ent[1]][0]['reqTime'] = 0
            if G[ent[0]][ent[1]][0]['direct'] == 2: G[ent[1]][ent[0]][0]['reqTime'] = 0

    print('Done with Optimization')

    return rec_ent_list


def temp_optimized_path(F, sources, targets, param):

    path = []
    _distribute_node_weight(F, param)
    for trg in targets:
        length_per_src = {src: nx.dijkstra_path_length(F, source=src, target=trg) for src in sources if nx.has_path(F, src, trg)}
        shortest = min(length_per_src, key=length_per_src.get)
        path.append(nx.dijkstra_path(F, shortest, trg))

    proc_steps = []
    for sp in path:
        i = 0
        for n in sp[1:]:
            if n not in proc_steps and F.nodes[n]['status'] == 'damaged':
                proc_steps.append(n)
            if (sp[i], sp[i+1]) not in proc_steps and F[sp[i]][sp[i+1]][0]['status'] == 'damaged':
                proc_steps.append((sp[i], sp[i+1]))
                i += 1

    return proc_steps


def hard_optimization(G, opt_param='reqTime', ent_type_pri=[]):

    if opt_param != 'reqTime':
        raise NotImplementedError

    K = copy.deepcopy(G)
    output = []
    pri_levels = sorted(set([K.nodes[n]['pri'] for n in K.nodes()]))
    sources = [node for node in K.nodes() if K.nodes[node]['type'] == 'source']

    if len(sources) == 0:
        raise ValueError("There is no sources (type=source) exist in the input data")


    for pr in pri_levels:
        if len(ent_type_pri) > 0:
            for hr in ent_type_pri:
                loc_out = [node for node in K.nodes() if K.nodes[node]['pri'] == pr and K.nodes[node]['type'] == hr
                           and K.nodes[node]['status']=='damaged']
                if len(loc_out) > 1:
                    loc_shortest_length = {}
                    for trg in loc_out:
                        length_per_src = {src: nx.dijkstra_path_length(K, source=src, target=trg) for src in sources if nx.has_path(K, src, trg)}
                        shortest = min(length_per_src, key=length_per_src.get)
                        loc_shortest_length[trg] = nx.dijkstra_path(K, shortest, trg)
                    loc_out = sorted(loc_shortest_length.keys(), key=lambda k: loc_shortest_length[k])
                output.extend(loc_out)
        else:
            loc_out = [node for node in K.nodes() if K.nodes[node]['pri'] == pr and K.nodes[node]['status']=='damaged']
            if len(loc_out) > 1:
                loc_shortest_length = {}
                for trg in loc_out:
                    length_per_src = {src: nx.dijkstra_path_length(K, source=src, target=trg) for src in sources if nx.has_path(K, src, trg)}
                    shortest = min(length_per_src, key=length_per_src.get)
                    loc_shortest_length[trg] = nx.dijkstra_path(K, shortest, trg)
                loc_out = sorted(loc_shortest_length.keys(), key=lambda k: loc_shortest_length[k])
            output.extend(loc_out)


    optimized_path = []
    for node in output:
        length_per_src = {src: nx.dijkstra_path_length(K, source=src, target=node) for src in sources if nx.has_path(K, src, node)}
        closest_src = min(length_per_src, key= lambda k: length_per_src[k])
        nodes_in_path = nx.dijkstra_path(K, closest_src, node)
        for n1, n2 in zip(nodes_in_path[:-1], nodes_in_path[1:]):
            if K[n1][n2][0]['status'] == 'damaged':
                optimized_path.append((n1, n2))
                K[n1][n2][0]['status'] = 'functional'
                K[n1][n2][0][opt_param] = 0
                if K[n1][n2][0]['direct'] == 2:
                    K[n2][n1][0]['status'] = 'functional'
                    K[n2][n1][0][opt_param] = 0

            if K.nodes[n2]['status'] == 'damaged':
                optimized_path.append(n2)
                K.nodes[n2]['status'] = 'functional'
                K.nodes[n2][opt_param] = 0

    for u, v in K.edges():
        if K[u][v][0]['status'] == 'damaged':
            optimized_path.append((u,v))
            K[u][v][0]['status'] = 'functional'
            K[u][v][0][opt_param] = 0
            if K[u][v][0]['direct'] == 2:
                K[v][u][0]['status'] = 'functional'
                K[v][u][0][opt_param] = 0

    print('number of damaged entities: ', len(optimized_path))

    return optimized_path


def parsing_ntw():

    parser = argparse.ArgumentParser(
        description='This function is used to find optimal recovery path',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-g',
                        '--graph',
                        type=str,
                        required=True,
                        help='insert graph')

    parser.add_argument('-s',
                        '--sources',
                        type=str,
                        required=True,
                        help='insert list of sources ')

    parser.add_argument('-t',
                        '--targets',
                        type=str,
                        required=True,
                        help='insert list of targets')

    parser.add_argument('-m',
                        '--method',
                        default='conventional',
                        type=str,
                        help='default - fix later')

    parser.add_argument('-o',
                        '--opt-param',
                        default='reqTime',
                        type=str,
                        help='default - fix later')

    parser.add_argument('-n',
                        '--norm-param',
                        default='reqExpr',
                        type=str,
                        help='default - fix later')

    args = parser.parse_args()

    return args.graph, args.sources, args.targets, args.method, args.opt_param, args.norm_param


def main():

    G, sources, targets, method, opt_param, norm_param = parsing_ntw()
    return


if __name__ == '__main__':

    main()