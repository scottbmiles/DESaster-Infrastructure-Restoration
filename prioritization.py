__version__ = "0.5"
__status__ = "In progress"


import optimization as opt


def user_defined_hard_prioritization(E):

    opt_restoration_list = []
    target_types = ['hv_sub', 'lv_sub']

    sources = [node for node in E.nodes() if E.nodes[node]['type'] == 'source']

    targets_p1 = [node for node in E.nodes() if E.nodes[node]['type'] in target_types
                   and E.nodes[node]['status']=='damaged' and E.nodes[node]['pri'] == 1]

    targets_p2 = [node for node in E.nodes() if E.nodes[node]['type'] in target_types
                   and E.nodes[node]['status']=='damaged' and E.nodes[node]['pri'] == 2]

    targets_p3 = [node for node in E.nodes() if E.nodes[node]['type'] in target_types
                   and E.nodes[node]['status']=='damaged' and E.nodes[node]['pri'] == 3]

    method = 'conventional'
    opt_param = 'reqTime'
    norm_param = 'reqExpr'

    print('pre-optimization')
    # priority 1:
    opt_restoration_list += opt.temp_optimized_path(E, sources, targets_p1, opt_param)
    print(targets_p1, opt_restoration_list)
    # priority 2:
    opt_restoration_list += opt.temp_optimized_path(E, sources, targets_p2, opt_param)
    print(targets_p2, opt_restoration_list)
    # priority 3:
    opt_restoration_list += opt.temp_optimized_path(E, sources, targets_p3, opt_param)
    print(targets_p3, opt_restoration_list)
    print('list of damaged entities to be fixed based on priorities: ',
          list(set(opt_restoration_list)))
    print(len(list(set(opt_restoration_list))))
    exit()

    return list(set(opt_restoration_list))


def main():

    #TODO: Parsing
    opt_list = user_defined_hard_prioritization(G)

    return opt_list


if __name__ == '__main__':

    main()