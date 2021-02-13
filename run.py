__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import get_infr_system_data as get_in
import infr_network as inw
import optimization as opt
import damage_detection as dmg
import time
import simpy as sp
import csv
import random
import viz
import hazard_evaluation as he
import resources_required_for_repair as rrr
import available_resources as ar
import os
import change_of_status as cos
import prioritization as pri
import monitoring
import process

###===========================================###
###=== Step0: Input/Output files =============###
###===========================================###
# make sure that required input files exist
node_dir = 'input/network_nodes.csv'
edge_dir = 'input/network_edges.csv'
crew_av_f = 'input/crew_availability.csv'
supply_av_f = 'input/supply_availability.csv'
budget_av_f = 'input/budget_availability.csv'

###===========================================###
###=== Step1: network generation =============###
###===========================================###

# generate the network

nodes = get_in.get_nodes(node_dir, 'Power')
edges = get_in.get_edges(edge_dir, 'Power')

E = inw.gen_graph(nodes, edges)

# to see the graph:
# viz.display_graph(E, show_or_save='save')

###=======================================###
###=== Step2: damage identification ======###
###=======================================###

E = dmg.user_defined_damage_state(E)

###=======================================###
###=== Step3: Available Resources ========###
###=======================================###
# get available resources

resources = ar.available_resources(crew_av_f, supply_av_f, budget_av_f)

###=======================================###
###=== Step4: Restoration sequence =======###
###=======================================###

# there are two types of prioritization implemented:
# 1- the inserted priority level
# 2- prioritization based on type of entities, e.g. entity_type_priority = ['hv_sub', 'lv_sub']
# ... which prioritizes high voltage substations over low voltage substations.
# if there is no entity-based prioritization, just use an empty array ([])
entity_type_priority = ['hv_sub', 'lv_sub']
opt_list = opt.hard_optimization(E, 'reqTime', entity_type_priority)

###=======================================###
###=== Step5: Process  ===================###
###=======================================###

process.processes_to_repair_sorted_entities(E, opt_list, resources)

###=======================================###
###=== Step6: Outputs ====================###
###=======================================###

monitoring.entity_status(E)
monitoring.recovery_timeframe(E)