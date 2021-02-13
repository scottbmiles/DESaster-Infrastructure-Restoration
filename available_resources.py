__version__ = "0.5"
__status__ = "In progress"

import networkx as nx
import argparse
import random
import numpy as np
import math


def deteremine_av_resources(method, mu, sigma):

    if method == 'uniform':
        return mu
    elif method == 'normDist':
        return max(int(random.normalvariate(mu, sigma)), 1)
    elif method == 'logNormDist':
        return max(int(random.lognormvariate(mu, sigma)), 1)
    else:
        print(method)
        raise ValueError("the inserted available resources are not invalid! It should be 'uniform', 'normDist', or 'logNormDist'")


def crew_availability(f_crew):

    crew_av = []
    try:
        with open(f_crew, 'r') as f:

            next(f)
            for row in f:
                row = row.split(',')
                time = int(row[0])
                val = deteremine_av_resources(row[3].strip('\n'), int(row[1]), int(row[2]))
                crew_av.append([time, val])

    except FileNotFoundError as error:
        print(error)

    return crew_av


def budg_availability(f_budg):

    budg_av = []
    try:
        with open(f_budg, 'r') as f:

            next(f)
            for row in f:
                row = row.split(',')
                time = int(row[0])
                val = deteremine_av_resources(row[3].strip('\n'), int(row[1]), int(row[2]))
                budg_av.append([time, val])

    except FileNotFoundError as error:
        print(error)

    return budg_av


def supply_availability(f_sup):

    sup_av = {}
    try:
        with open(f_sup, 'r') as f:

            next(f)
            for row in f:
                row = row.split(',')
                sup_av[row[0]] = {
                    'in_stock': [int(row[1]), int(row[2]), int(row[3])],
                    'out_of_stock': [int(row[4]), int(row[5]), int(row[6])]
                }

    except FileNotFoundError as error:
        print(error)

    return sup_av


def available_resources(f_crew, f_supply, f_budget):

    res = {}
    res['av_crews'] = crew_availability(f_crew)
    res['av_eqp'] = supply_availability(f_supply)
    res['av_budg'] = budg_availability(f_budget)

    return res


def main():

    res = available_resources(f_crew, f_supply, f_budget)

    return res


if __name__ == '__main__':

    main()