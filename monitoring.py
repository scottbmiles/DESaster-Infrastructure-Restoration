__version__ = "0.5"
__status__ = "In progress"

from functools import partial, wraps
import simpy
import csv
import os


def write_req_crews(time, entity, av_crews, req_crews, file="output/report.txt"):

    text = "{} : request for {} crews to repair {} while {} crews are available".format(time, req_crews, entity, av_crews)
    print(text)

def write_transfer_crews(time, entity, req_crews, arrival_t):

    text = "{}: {} crews are being transferred to {} and will get to the site at {}".format(time, req_crews, entity, arrival_t)
    print(text)


def write_req_eqp(time, item, eqp, level):

    text = "{}: {} requested for a {} while {} is available".format(time, item, eqp, level)
    print(text)


def write_received_eqp(time, ent):

    text = "{}: {} received required equipment".format(time, ent)
    print(text)


def write_start_repair(time, req_crews, entity, dt):

    text = "{}: {} crews got to the site and started repairing {} which will be fixed at {}".format(time, req_crews,
                                                                            entity, time + dt)
    print(text)

def write_end_of_repair(time, entity, req_crews, av_crews):

    text = "{}: repair of {} is done and {} crews released- {} crews are available".format(time, entity, req_crews, av_crews)
    print(text)

def write_update_number_of_crews(time, d_crews, av_crews):

    text = "{}: update on number of crews: {} crews are {} and {} crews are available then".format(time, abs(d_crews),
                "added" if d_crews > 0 else "excluded", av_crews)
    print(text)

# def track_expenses(time, action, cost, output=None, fout=None):
#
#     if fout is None:
#         fout = 'output/cost_time.csv'
#
#     if output is None:
#         output = []
#
#     output.append([time, cost*1000, action])
#
#     with open(fout, 'a', newline="") as f:
#         writer = csv.writer(f)
#         writer.writerows(output)
#
#     return output


def entity_status(G, fout=None):

    if fout is None:
        fout = 'output/entity_status.csv'

    output = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    max_t = (max([val['operational'] for key, val in output.items()])//10 + 1)*10
    output = [[key, val['pre'], val['damaged'], val['processing'], val['functional'], val['operational'], max_t]
           for key, val in output.items()]
    output.sort(key=lambda x: x[2])

    with open(fout, 'w+', newline="") as f:
        header = ['entity', 'pre', 'damaged', 'processing', 'functional', 'operational', 'end']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(output)

    # record recovery timeframe based on priority level
    pri_list = []
    for i in range(len(output)):
        node = output[i][0]
        if node in G.nodes():
            dmg = 1 if output[i][4] > 0 else 0
            pri_list.append([node, G.nodes[node]['pri'], output[i][4], output[i][5], dmg])


def recovery_timeframe(G, fout=None):

    if fout is None:
        fout = 'output/recovery_timeframe.csv'

    # step 1: based on both nodes and edges
    outnodes = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    output = {}
    output.update(outnodes)
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    max_t = (max([val['operational'] for key, val in output.items()])//10 + 1)*10 + 1

    tf = []
    tf.append((-10, 0, 0, len(output), len(output), 0, 0, len(outnodes), len(outnodes)))
    tf.append((-0.0001, 0, 0, len(output), len(output), 0, 0, len(outnodes), len(outnodes)))

    for t in range(max_t):
        # all entities
        n_dmg = sum([1 if val['processing'] > t else 0 for val in output.values()])
        n_prc = sum([1 if val['processing'] <= t < val['functional'] else 0 for val in output.values()])
        n_fnc = sum([1 if val['functional'] <= t else 0 for val in output.values()])
        n_opr = sum([1 if val['operational'] <= t else 0 for val in output.values()])

        # only substations
        p_dmg = sum([1 if val['processing'] > t else 0 for val in outnodes.values()])
        p_prc = sum([1 if val['processing'] <= t < val['functional'] else 0 for val in outnodes.values()])
        p_fnc = sum([1 if val['functional'] <= t else 0 for val in outnodes.values()])
        p_opr = sum([1 if val['operational'] <= t else 0 for val in outnodes.values()])

        tf.append((t, n_dmg, n_prc, n_fnc, n_opr, p_dmg, p_prc, p_fnc, p_opr))

    with open(fout, 'w+', newline="") as f:
        header = ['time', 'all_damaged', 'all_processing', 'all_functional', 'all_operational', 'node_damaged', 'node_processing', 'node_functional', 'node_operational']
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(tf)


def sensitivity_outside_crews_summary(G, fout=None, t_max=None, t_max_nominal = 200, t0=0, dt=0, n_subs=35, n_ent=79, cd=5000):

    # step 1: based on both nodes and edges
    outnodes = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    output = {}
    output.update(outnodes)
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    if t_max is None:
        t_max =  max([val['operational'] for key, val in output.items()])

    subs_f, subs_o, tot_f, tot_o = [0, 0, 0, 0]
    for t in range(t_max):

        # all entities
        n_fnc = sum([1 if val['functional'] <= t else 0 for val in output.values()])
        n_opr = sum([1 if val['operational'] <= t else 0 for val in output.values()])

        # only substations
        p_fnc = sum([1 if val['functional'] <= t else 0 for val in outnodes.values()])
        p_opr = sum([1 if val['operational'] <= t else 0 for val in outnodes.values()])

        subs_f += p_fnc
        subs_o += p_opr
        tot_f += n_fnc
        tot_o += n_opr

    subs_f2, subs_o2, tot_f2, tot_o2 = [0, 0, 0, 0]
    for t in range(t_max_nominal):

        # all entities
        n_fnc2 = sum([1 if val['functional'] <= t else 0 for val in output.values()])
        n_opr2 = sum([1 if val['operational'] <= t else 0 for val in output.values()])

        # only substations
        p_fnc2 = sum([1 if val['functional'] <= t else 0 for val in outnodes.values()])
        p_opr2 = sum([1 if val['operational'] <= t else 0 for val in outnodes.values()])

        subs_f2 += p_fnc2
        subs_o2 += p_opr2
        tot_f2 += n_fnc2
        tot_o2 += n_opr2

    out_print = [t0, dt, cd, t_max, subs_f / n_subs, subs_o / n_subs, tot_f / n_ent, tot_o / n_ent,
                 subs_f / (t_max * n_subs), subs_o / (t_max * n_subs), tot_f / (t_max * n_ent), tot_o / (t_max * n_ent),
                 subs_f2 / (t_max_nominal * n_subs), subs_o2 / (t_max_nominal * n_subs), tot_f2 / (t_max_nominal * n_ent), tot_o2 / (t_max_nominal * n_ent),
                 ]
    header = ['t0', 'dt', 'crew_day', 'rec_time', 'idx_subs_f', 'idx_subs_o', 'idx_tot_f', 'idx_tot_o',
              'norm_tmax_subsf', 'norm_tmax_subso', 'norm_tmax_totf', 'norm_tmax_toto',
              'norm_tN_subsf', 'norm_tN_subso', 'norm_tN_totf', 'norm_tN_toto',
              ]

    if fout is None:
        fout = 'output/summary.csv'

    with open(fout, 'a+', newline="") as f:
        writer = csv.writer(f)
        if os.stat(fout).st_size == 0:
            writer.writerow(header)
        writer.writerow(out_print)


def sensitivity_inside_crews_summary(G, fout=None, in_crews=0, n_dmg=0, n_tot=79):

    # step 1: based on both nodes and edges
    outnodes = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    output = {}
    output.update(outnodes)
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    t_max_exact = max([val['operational'] for key, val in output.items()])

    header = ['damage(%)', 'n_crews', 'rec_time']
    with open(fout, 'a+', newline="") as f:
        writer = csv.writer(f)
        if os.stat(fout).st_size == 0:
            writer.writerow(header)
        writer.writerow([n_dmg/n_tot, in_crews, t_max_exact])

    return


def sensitivity_damage_summary(G, fout=None, dmg=0.5, count=None, std_tmax=None, n_subs=39, n_ent=79, n_dmg=None):

    # step 1: based on both nodes and edges
    outnodes = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    output = {}
    output.update(outnodes)
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    max_t = max([val['operational'] for key, val in output.items()])

    subs_f, subs_o, tot_f, tot_o = [0, 0, 0, 0]
    for t in range(max_t):

        # all entities
        n_fnc = sum([1 if val['functional'] <= t else 0 for val in output.values()])
        n_opr = sum([1 if val['operational'] <= t else 0 for val in output.values()])

        # only substations
        p_fnc = sum([1 if val['functional'] <= t else 0 for val in outnodes.values()])
        p_opr = sum([1 if val['operational'] <= t else 0 for val in outnodes.values()])

        subs_f += p_fnc
        subs_o += p_opr
        tot_f += n_fnc
        tot_o += n_opr

    subs_f_std, subs_o_std, tot_f_std, tot_o_std = [0, 0, 0, 0]
    for t in range(std_tmax):

        # all entities
        n_fnc_std = sum([1 if val['functional'] <= t else 0 for val in output.values()])
        n_opr_std = sum([1 if val['operational'] <= t else 0 for val in output.values()])

        # only substations
        p_fnc_std = sum([1 if val['functional'] <= t else 0 for val in outnodes.values()])
        p_opr_std = sum([1 if val['operational'] <= t else 0 for val in outnodes.values()])

        subs_f_std += p_fnc_std
        subs_o_std += p_opr_std
        tot_f_std += n_fnc_std
        tot_o_std += n_opr_std

    out_print = [dmg, n_dmg, max_t, subs_f/(n_subs*max_t), subs_o/(n_subs*max_t), tot_f/(n_ent*max_t), tot_o/(n_ent*max_t), subs_f_std/(n_subs*std_tmax), subs_o_std/(n_subs*std_tmax), tot_f_std/(n_ent*std_tmax), tot_o_std/(n_ent*std_tmax)]

    if fout is None:
        fout = 'output/sensitivity_damage/summary.csv'

    header = ['damage(%)', 'damage(#)', 't_max', 'subs_fnc_rate_tmax', 'subs_opr_rate_tmax', 'entities_fnc_rate_tmax', 'entities_opr_rate_tmax', 'subs_fnc_rate_t100', 'subs_opr_rate_t100', 'entities_fnc_rate_t100', 'entities_opr_rate_t100']

    with open(fout, 'a+', newline="") as f:
        writer = csv.writer(f)
        if count == 0:
            writer.writerow(header)
        writer.writerow(out_print)


def sensitivity_equipment_summary(G, fout=None, dmg=0.5, n_dmg=None, count=None, stored_res={}, out_sum=[], dmg_ent={}):

    # step 1: based on both nodes and edges
    outnodes = {n: G.nodes[n]['output'] for n in G.nodes() if G.nodes[n]['type'] != 'source'}
    output = {}
    output.update(outnodes)
    prev = []
    for u, v in G.edges():
        if (v, u) not in prev:
            output[(u,v)] = G[u][v][0]['output']
            prev.append((u,v))

    max_t = max([val['operational'] for key, val in output.items()])
    out_print = [n_dmg, stored_res['cost'], max_t, stored_res['hv_sub'], stored_res['lv_sub'], stored_res['hv_tran'], stored_res['lv_tran'],
                 dmg_ent['hv_sub'], dmg_ent['lv_sub'], dmg_ent['hv_tran'], dmg_ent['lv_tran']]
    out_sum.append(out_print)

    header = ['damage(#)', 'cost', 't_max', 'hv_sub_av', 'lv_sub_av', 'hv_tran_av', 'lv_tran_av', 'hv_sub_dmg', 'lv_sub_dmg', 'hv_tran_dmg', 'lv_tran_dmg']

    with open(fout, 'a+', newline="") as f:
        writer = csv.writer(f)
        if count == 0:
            writer.writerow(header)
        writer.writerow(out_print)

    return out_sum


def sensitivity_equipment_summary_2(out_list, fout, count):

    i = len(out_list)-1
    while out_list[i][2] == out_list[i-1][2]:
        i -= 1

    header = ['damage(#)', 'cost', 't_max', 'hv_sub_av', 'lv_sub_av', 'hv_tran_av', 'lv_tran_av', 'hv_sub_dmg', 'lv_sub_dmg', 'hv_tran_dmg', 'lv_tran_dmg']

    with open(fout, 'a+', newline="") as f:
        writer = csv.writer(f)
        if count == 0:
            writer.writerow(header)
        writer.writerow(out_list[i])


def restoration_cost(G):

    return 0





