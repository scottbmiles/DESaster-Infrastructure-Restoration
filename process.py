__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import matplotlib.pyplot as plt
import simpy
import json
import viz
import numpy as np
import random
import monitoring
import change_of_status as cos


def crews_availability_process(env, av_crews, state):

    av_crews_0 = av_crews if state == 'static' else av_crews[0][1]
    res_crews = simpy.Container(env, init=av_crews_0)

    if state == 'dynamic':
        env.process(crews_availability_process_dynamic(env, av_crews, res_crews))

    return res_crews


def crews_availability_process_dynamic(env, av_crews, res_crews):

    i = 1
    for t,v in av_crews[1:]:
        dt_out = t - av_crews[i-1][0]
        yield env.timeout(dt_out)
        d_crews = v - av_crews[i-1][1]
        if d_crews > 0:
            res_crews.put(d_crews)
            # monitoring.write_update_number_of_crews(time=env.now, d_crews=d_crews, av_crews=res_crews.level)

        else:
            res_crews.get(-d_crews)
            # monitoring.write_update_number_of_crews(time=env.now, d_crews=d_crews, av_crews=res_crews.level)
        i += 1

    return res_crews


def equipment_availability_process(env, av_eqp, req_eqp, state):

    if state != 'dynamic':
        raise NotImplementedError

    hv_sub0 = av_eqp['hv_sub']['in_stock']
    lv_sub0 = av_eqp['lv_sub']['in_stock']
    hv_tran0 = av_eqp['hv_tran']['in_stock']
    lv_tran0 = av_eqp['lv_tran']['in_stock']

    res_eqp = {
        'hv_sub': simpy.Container(env, init=hv_sub0[0]),
        'lv_sub': simpy.Container(env, init=lv_sub0[0]),
        'hv_tran':simpy.Container(env, init=hv_tran0[0]),
        'lv_tran':simpy.Container(env, init=lv_tran0[0])
    }

    # # # track expenses
    # for key in res_eqp.keys():
    #     monitoring.track_expenses(env.now, 'in_stock_eqp', av_eqp[key]['in_stock'][1])

    req_out_of_stock = {}

    # print('req_eqp:', req_eqp)
    for key, val in req_eqp.items():
        if val > av_eqp[key]['in_stock'][0]:
            req_out_of_stock[key] = [val - av_eqp[key]['in_stock'][0],
                                     av_eqp[key]['out_of_stock'][1],
                                     av_eqp[key]['out_of_stock'][2]]
        else:
            req_out_of_stock[key] = [0, 0, 0]

    env.process(equipment_availability_process_dynamic(env, req_out_of_stock, res_eqp))

    return res_eqp


def equipment_availability_process_dynamic(env, av_eqp_out, res_eqp):

    for key in av_eqp_out:

        if av_eqp_out[key][0] > 0 :
            # print('{}: ordered {} which will be at site at {}'.format(env.now, key, env.now + av_eqp_out[key][1]))
            yield env.timeout(av_eqp_out[key][1])
            # monitoring.track_expenses(env.now, 'out_of_stock_eqp', av_eqp_out[key][2])
            # print('{}: {} shipped at {}'.format(env.now, key, env.now))
            res_eqp[key].put(av_eqp_out[key][0])


def budget_availability_process(env, av_budg, state):

    av_budg_0 = av_budg if state == 'static' else av_budg[0][1]
    res_budg = simpy.Container(env, init=av_budg_0)
    if state != 'static':
        env.process(budget_availability_process_dynamic(env, av_budg, res_budg))

    return res_budg


def budget_availability_process_dynamic(env, av_budg, res_budg):

    i = 1
    for t,v in av_budg[1:]:
        dt_out = t - av_budg[i-1][0]
        yield env.timeout(dt_out)
        d_budg = v - av_budg[i-1][1]
        if d_budg > 0:
            yield res_budg.put(d_budg)
            # print(env.now, ': update: {} budget are added'.format(d_budg))
        else:
            # print(env.now, ': Request to exclude {} budget'.format(d_budg))
            yield res_budg.get(-d_budg)
            # print(env.now, ': update: {} budget are excluded'.format(-d_budg))

    return res_budg


# step 3: implement repair process
class Repair_Entity(object):

    def __init__(self, env, G, ent_name, ent, res_exp, res_eqp, res_bdg,
                 t_assess=0, t_plan=0, t_access=0, t_ship_eqp=0, t_transfer_crews=0):
        self.env = env
        self.G = G
        self.ent = ent
        self.ent_name = ent_name
        self.t_assess = t_assess
        self.t_plan = t_plan
        self.t_access = t_access
        self.t_ship_eqp = t_ship_eqp
        self.t_transfer_crews = t_transfer_crews
        self.t_repair = ent['reqTime']
        self.req_crews = ent['reqExpr']
        self.req_eqp = ent['reqEqp']
        self.res_exp = res_exp
        self.res_eqp = res_eqp
        self.res_bdg = res_bdg

    # 1: damage assessment
    # USE THIS ONLY IF IT HAS timeout for different entities
    def damage_assessment(self):
        # print(self.env.now, ': damage assessment started- entity:', self.ent['id'])
        yield self.env.timeout(self.t_assess)
        # print(self.env.now, ': damage assessment ended- entity:', self.ent['id'])

    # 3: plan for repair
    # USE THIS ONLY IF IT HAS timeout for different entities
    def plan_for_rep(self):
        # print(self.env.now, ': planning started- entity:', self.ent['id'])
        yield self.env.timeout(self.t_plan)
        # print(self.env.now, ': planning ended- entity:', self.ent['id'])

    # 4: request for supply
    def request_for_equipment(self):

        # print('{}: requested for equipments for {}'.format(self.env.now, self.ent_name))
        # if self.res_eqp[self.ent['reqEqp']].level > 0:
        # print(self.ent['reqEqp'], self.res_eqp[self.ent['reqEqp']].level)
        # monitoring.write_req_eqp(self.env.now, self.ent_name, self.ent['reqEqp'], self.res_eqp[self.ent['reqEqp']].level)
        yield self.res_eqp[self.ent['reqEqp']].get(1)
        # monitoring.write_received_eqp(self.env.now, self.ent_name)
        # print('{}: {} received equipment and waiting for crews to start restoration'.format(self.env.now, self.ent_name))
        # print('{}: {} {} are available'.format(self.env.now, self.res_eqp[self.ent['reqEqp']].level, self.ent['reqEqp']))


    # 4-b: add a process if the site is not accessible for a while!
    def wait_for_accessibility(self):
        # print(self.env.now, ': waiting for access started- entity:', self.ent['id'],
        #       self.res_exp.level)
        yield self.env.timeout(self.t_access)
        # monitoring.write_output([self.env.now, self.ent['id'], 'got access to', self.ent['status']])
        # print(self.env.now, ': waiting for access ended- entity:', self.ent['id'],
        #       self.res_exp.level)


    # 5: request for crews
    def request_for_crews(self):
        # request for available crews
        # monitoring.write_req_crews(time=self.env.now, entity=self.ent['id'], av_crews=self.res_exp.level,
        #                            req_crews=self.req_crews)
        # while self.res_exp.level < self.req_crews:
        #     self.env.timeout(1)
        yield self.res_exp.get(self.req_crews)
        # monitoring.write_transfer_crews(time=self.env.now, entity=self.ent['id'], req_crews=self.req_crews,
        #                                 arrival_t = self.env.now + self.t_transfer_crews)
        yield self.env.timeout(self.t_transfer_crews)
        # monitoring.write_start_repair(time=self.env.now, req_crews=self.req_crews, entity=self.ent['id'], dt=self.t_repair)


    # 6: the repair
    def repair_entity(self):
        # time to do the repair
        # change of status: damaged to processing
        cos.entity_change_of_status(self.G, self.ent_name, 'processing', self.env.now)
        yield self.env.timeout(self.t_repair)
        # monitoring.track_expenses(self.env.now, 'restoration of {}'.format(self.ent_name), self.ent['reqBudg'])
        yield self.res_exp.put(self.req_crews)
        # monitoring.write_end_of_repair(self.env.now, entity=self.ent_name, req_crews=self.req_crews, av_crews=self.res_exp.level)
        cos.entity_change_of_status(self.G, ent=self.ent_name, new_status='functional', time=self.env.now)
        cos.change_of_status_based_on_source(self.G, self.env.now)
        # viz.display_graph(self.G, show_or_save='save', time=self.env.now)


def find_required_equipment(G):

    eqp_list = []

    for n in G.nodes():
        if G.nodes[n]['status'] == 'damaged' and G.nodes[n]['reqEqp'] not in eqp_list:
            eqp_list.append(G.nodes[n]['reqEqp'])

    for u, v in G.edges():
        if G[u][v][0]['status'] == 'damaged' and G[u][v][0]['reqEqp'] not in eqp_list:
            eqp_list.append(G[u][v][0]['reqEqp'])

    req_eqp = {eqp:0 for eqp in eqp_list}

    for n in G.nodes():
        if G.nodes[n]['status'] == 'damaged':
            req_eqp[G.nodes[n]['reqEqp']] += 1

    prev = []
    for u, v in G.edges():
        if G[u][v][0]['status'] == 'damaged' and (v, u) not in prev:
            req_eqp[G[u][v][0]['reqEqp']] += 1
            prev.append((u, v))

    return req_eqp


def equipment_availability_process3(env, av_eqp, req_eqp, state, key, res_eqp={}):

    if state != 'dynamic':
        raise NotImplementedError

    eqp = av_eqp[key]['in_stock'][0]
    if key not in res_eqp.keys():
        res_eqp[key] = simpy.Container(env, init=eqp)
    val = req_eqp[key]
    if val > av_eqp[key]['in_stock'][0]:
            # print('{}: ordered {} which will be at site at {}'.format(env.now, key, env.now + av_eqp[key]['out_of_stock'][1]))
            # monitoring.track_expenses(env.now, 'out_of_stock', av_eqp[key]['out_of_stock'][2]*(val - av_eqp[key]['in_stock'][0]))
            yield env.timeout(av_eqp[key]['out_of_stock'][1])
            # print('{}: {} shipped at {}'.format(env.now, key, env.now))
            res_eqp[key].put(val - av_eqp[key]['in_stock'][0])

    return res_eqp


def restoration_process(env, G, ent_list, req_eqp, av_res):

    res_crews = crews_availability_process(env, av_res['av_crews'], 'dynamic')
    res_budg = budget_availability_process(env, av_res['av_budg'], 'dynamic')

    res_eqp = {}
    for key in av_res['av_eqp'].keys():
        env.process(equipment_availability_process3(env, av_res['av_eqp'], req_eqp, 'dynamic', key, res_eqp))

    ent_events = []
    eqp_events = []
    for ent in ent_list:

        ent_data = G.nodes[ent] if ent in G.nodes() else G[ent[0]][ent[1]][0]
        ent_repair_proc = Repair_Entity(env, G, ent, ent_data, res_crews, res_eqp, res_budg,
                                        t_transfer_crews=0)
        ent_events.append(ent_repair_proc)

        eqp_events.append(env.process(ent_repair_proc.request_for_equipment()))


    for ent_ev, eqp_ev in zip(ent_events, eqp_events):
        yield eqp_ev & env.process(ent_ev.request_for_crews())
        env.process(ent_ev.repair_entity())


def processes_to_repair_sorted_entities(G, ent_l, av_res):

    """
    This function ....
    """

    # step 1: define simpy process
    env = simpy.Environment()

    # step 2: define resources
    req_eqp = find_required_equipment(G)

    # step 3: define the restoration process
    env.process(restoration_process(env, G, ent_l, req_eqp=req_eqp, av_res=av_res))

    # step 4: changes of resources over time
    env.run()