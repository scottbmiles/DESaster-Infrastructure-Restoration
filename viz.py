#temp


import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import glob
from numpy import sqrt
import glob
import os
import numpy as np
from matplotlib.animation import FuncAnimation
import csv
from scipy.interpolate import griddata
import matplotlib.ticker as ticker

def display_graph(F, show_or_save='save', time=0, count=[0]):

    # to generate consistent file name
    count[0] += 1

    # pos for nodes:
    pos = {node:F.nodes[node]['pos'] for node in F.nodes()}

    # source list used for square shape
    src_list = [n for n in F.nodes() if F.nodes[n]['type']=='source']

    # color of nodes
    node_color = []

    for node in F.nodes():

        if F.nodes[node]['status']=='damaged':
            node_color.append('r')
        elif F.nodes[node]['status']=='processing':
            node_color.append('y')
        elif F.nodes[node]['status']=='functional':
            node_color.append('b')
        elif F.nodes[node]['status']=='operational':
            node_color.append('g')
        else:
            raise ValueError

    # color of edges
    edge_color = []
    for u,v in F.edges():
        if F[u][v][0]['status']=='damaged':
            edge_color.append('r')
        elif F[u][v][0]['status']=='processing':
            edge_color.append('y')
        elif F[u][v][0]['status']=='functional':
            edge_color.append('b')
        elif F[u][v][0]['status']=='operational':
            edge_color.append('g')
        else:
            raise ValueError

    # edge thickness
    widths = [4 if F[u][v][0]['type']=='HV' else 2 for u,v in F.edges()]

    # node size
    node_size = [200 if F.nodes[n]['type']=='source' else 150 if F.nodes[n]['type']=='hv_sub' else 60 for n in F.nodes()]

    nx.draw_networkx(F,pos,width=widths,alpha=1,node_color=node_color, edge_color=edge_color,
                     node_size=node_size, with_labels=False) #node_color=node_color,edge_color=edge_color,
    nx.draw_networkx_nodes(F,pos,alpha=1,nodelist=src_list,node_color='g',node_size=250, node_shape='s', with_labels=False) #node_color=node_color,edge_color=edge_color,
    ax=plt.gca()
    fig=plt.gcf()
    plt.axis('off')
    # plt.title('time: {}'.format(time))
    if show_or_save == 'show':
        plt.show()
    else:
        plt.savefig('output/recovery_network/{}_{}.eps'.format(time, count[0]), format='eps')
        plt.clf()


def scatter_plot_from_csv(f, ix=0, x_f=float, x_label='Percentage of Damage',
                          iy=1, y_f=int, y_label='Number of Local Crews',
                          iz=2, z_f=int, z_label='Restoration Time (days)', title='Recovery'):

    x, y, z = [], [], []

    with open(f, 'r') as csvf:
        reader = csv.reader(csvf)
        headers = next(reader, None)
        for row in reader:
            x.append(x_f(row[ix]))
            y.append(y_f(row[iy]))
            z.append(z_f(row[iz]))


    fig = plt.scatter(x, y, s=10, c=z, cmap='jet')
    plt.colorbar(fig, label=z_label)
    fig = plt.gca()
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xlim([0, 1.0])
    plt.ylim([100, 500])
    # formatter = ticker.FormatStrFormatter('%1.0f')

    fig.xaxis.set_major_formatter(ticker.PercentFormatter(1))
    # plt.title(title)
    plt.show()


def recovery_timeframe(rtf):

    # print(rtf, len(rtf), rtf[2][0])
    rtf.append([rtf[-1][0]+10, rtf[-1][1], 0, 1.0, '---', 'Fully-recovered'])

    t = np.array([rtf[i][0] for i in range(len(rtf))])
    x = np.array([rtf[i][3] for i in range(len(rtf))])
    label = [rtf[i][4] for i in range(len(rtf))]
    plt.title('Recovery Time-frame')
    plt.xlabel('Time (days)')
    plt.ylabel('Resilience Index')
    plt.plot(t,x, linewidth=2.5)
    plt.axis('on')
    plt.ylim([0, 1.0])
    plt.show()
    plt.savefig('recovery time-frame (operational entities per total entities).png')


def network_in_recovery_process(F, title, count=[0]):

    count[0]+=1
    # display network system with icons for entites
    icons = {}
    #TODO: display edges with icons:
    # https://gist.github.com/shobhit/3236373
    path = 'icons/'
    # generator icons for different status
    opr_gen_icon = (path+'generator-operational.png') # operational generator icon
    inopr_gen_icon = (path+'generator-inoperative.png') # inoperative generator icon
    proc_gen_icon = (path+'generator-processing.png') # processing generator icon
    wait_gen_icon = (path+'generator-waiting.png') # waiting generator icon
    dmg_gen_icon = (path+'generator-damaged.png') # damaged generator icon

    # substation icons for different status
    opr_subs_icon = (path+'substation-operational.png') # operational substation icon
    inopr_subs_icon = (path+'substation-inoperative.png') # inoperative substation icon
    proc_subs_icon = (path+'substation-processing.png') # processing substation icon
    wait_subs_icon = (path+'substation-waiting.png') # waiting substation icon
    dmg_subs_icon = (path+'substation-damaged.png') # damaged substation icon

    # customer icons for different status
    opr_cust_icon = (path+'customer-operational.png') # operational customer icon
    inopr_cust_icon = (path+'customer-inoperative.png') # inoperative customer icon
    proc_cust_icon = (path+'customer-processing.png') # processing customer icon
    wait_cust_icon = (path+'customer-waiting.png') # waiting customer icon
    dmg_cust_icon = (path+'customer-damaged.png') # damaged customer icon

    # reading icons
    icons = {
        'generator-damaged': mpimg.imread(dmg_gen_icon),
        'generator-waiting': mpimg.imread(wait_gen_icon),
        'generator-processing': mpimg.imread(proc_gen_icon),
        'generator-inoperative': mpimg.imread(inopr_gen_icon),
        'generator-operational': mpimg.imread(opr_gen_icon),

        'substation-damaged': mpimg.imread(dmg_subs_icon),
        'substation-waiting': mpimg.imread(wait_subs_icon),
        'substation-processing': mpimg.imread(proc_subs_icon),
        'substation-inoperative': mpimg.imread(inopr_subs_icon),
        'substation-operational': mpimg.imread(opr_subs_icon),

        'customer-damaged': mpimg.imread(dmg_cust_icon),
        'customer-waiting': mpimg.imread(wait_cust_icon),
        'customer-processing': mpimg.imread(proc_cust_icon),
        'customer-inoperative': mpimg.imread(inopr_cust_icon),
        'customer-operational': mpimg.imread(opr_cust_icon),
    }

    # draw with images on nodes

    # pos for nodes:
    pos = {node:F.nodes[node]['pos'] for node in F.nodes()}

    # color for edges
    color = []
    for u,v in F.edges():
        if F[u][v][0]['status']=='damaged':
            color.append('#%02x%02x%02x' % (237, 28, 36))
        elif F[u][v][0]['status']=='waiting':
            color.append('#%02x%02x%02x' % (200, 50, 60))
        elif F[u][v][0]['status']=='processing':
            color.append('#%02x%02x%02x' % (255, 242, 0))
        elif F[u][v][0]['status']=='inoperative':
            color.append('#%02x%02x%02x' % (0, 0, 255))
        else:
            color.append('#%02x%02x%02x' % (181, 230, 29))
            # color.append('g')

    # widths = []
    # for u,v in F.edges():
    #     if F[u][v][0]['type']=='HV_transmission':
    #         widths.append(7)
    #     elif F[u][v][0]['type']=='MV_transmission':
    #         widths.append(5)
    #     else:
    #         widths.append(3)

    nx.draw_networkx(F,pos,width=3 ,edge_color=color,alpha=0.6, with_labels=False)
    ax=plt.gca()
    fig=plt.gcf()
    plt.axis('off')
    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    imsize = 0.05 # this is the icon size
    for n in F.nodes():
        (x,y) = pos[n]
        xx,yy = trans((x,y)) # figure coordinates
        xa,ya = trans2((xx,yy)) # axes coordinates
        a = plt.axes([xa-imsize/2.0,ya-imsize/2.0, imsize, imsize])
        a.imshow(icons['-'.join([F.nodes[n]['type'], F.nodes[n]['status']])])
        a.set_aspect('equal')
        a.axis('off')
        a.set_title(F.nodes[n]['id'])
        a.set_frame_on(False)

    # plt.text(0,-20,s=title, bbox=dict(facecolor='red', alpha=2),horizontalalignment='center',
    #          verticalalignment='top')
    # plt.show()
    # plt.axis('off')
    plt.savefig(''.join(['plot4/', str(count[0]),'.png']), bbox_inches='tight')
    plt.clf()


def plot_resources():

    x = [0, 19.9999, 20, 49.9999, 50, 100]
    y = [100, 100, 250, 250, 100, 100]

    # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(6, 6))
    # plt.plot(x, 100)
    plt.plot(x, y, color='black', linewidth=2)
    ax = plt.fill_between(x, y, 100, color='yellow')
    ax2 = plt.fill_between(x, 0, 100, color='lightblue')
    plt.xlabel('Time (day)')
    plt.ylabel('Number of Crews')
    plt.xticks([])
    plt.yticks([])
    plt.legend((ax2, ax), ('Inside Crews', 'Outside Crews'))
    plt.xlim((0,100))
    plt.ylim((0, 300))
    plt.show()


def plot_crews():

    # x = [0, 9.9999, 10, 19.9999, 20, 39.9999, 40, 49.9999, 50, 59.9999, 60, 100]
    # y = [100, 100, 200, 200, 250, 250, 160, 160, 130, 130, 100, 100]

    x = [0, 19.9999, 20, 49.9999, 50, 100]
    y = [100, 100, 250, 250, 100, 100]


    # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(6, 6))
    # plt.plot(x, 100)
    plt.plot(x, y, color='black', linewidth=1)
    ax = plt.fill_between(x, y, 100, color='lightgray')
    ax2 = plt.fill_between(x, 0, 100, color='gray')
    plt.xlabel('Time (days)')
    plt.ylabel('Number of Crews')
    plt.xticks([])
    plt.yticks([])
    plt.legend((ax2, ax), ('local', 'non-local'))
    plt.xlim((0, 100))
    plt.ylim((0, 300))
    plt.show()


def sigmoid(a, b, c, x):

    return a + (1 - a) / (1 + np.exp(b*(c-x)))


def plot_recovery_index(tmax=200):

    n = 100
    x = np.linspace(0, tmax + 50, n, endpoint=True)
    a0 = 0.2
    b0 = 0.04
    x0 = 120
    y = sigmoid(a0, b0, x0, x)

    # ax0 = plt.plot(x, y, color='m')
    ax0 = plt.plot(x, y, color='black')

    a1 = 0.16
    b1 = 0.035
    x1 = 80
    z = sigmoid(a1, b1, x1, x)

    # ax1 = plt.plot(x, z, color='olive')

    # plt.text(2, 6, r'an equation: $E=mc^2$', fontsize=15)
    # plt.plot(x, np.ones_like(x), color='black', linestyle='dashed')

    # y = [100, 100, 250, 250, 100, 100]
    #
    # # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(6, 6))
    # # plt.plot(x, 100)
    # plt.plot(x, y, color='black', linewidth=2)
    ax = plt.fill_between(x, y, 0, color='yellow', where= x < 200)
    # ax2 = plt.fill_between(x, 0, 100, color='lightblue')
    plt.xlabel('Time(day)')
    plt.ylabel('Recovery Index')
    # plt.text(3, 3, 'r(t)')
    # plt.xticks([])
    # plt.yticks([])
    # plt.legend((ax2, ax), ('Inside Crews', 'Outside Crews'))
    # plt.legend( ('Late Arrival Crews', 'Early arrival Crews'))
    plt.xlim((0, 200))
    plt.ylim((0, 1.0))
    plt.show()


def plot_intensity_tmax(f, x_idx=0, y_idx=2, x_frm=float, y_frm=int, x_label='damage intensity (%)',
                        y_label='recovery time (day)'):

    x, y = [], []

    with open(f, 'r') as csvf:
        reader = csv.reader(csvf)
        headers = next(reader, None)
        for row in reader:
            x.append(x_frm(row[x_idx]))
            y.append(y_frm(row[y_idx]))
    # fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True, figsize=(6, 6))
    # plt.plot(x, 100)
    # plt.scatter(x, y, color='blue', s=1)
    # fit a linear curve an estimate its y-values and their error.
    x = np.array(x)
    y = np.array(y)
    a, b, c, d = np.polyfit(x, y, deg=3)
    y_est = a * x ** 3 + b * x ** 2 + c * x + d
    # y_err = x.std() * np.sqrt(1/len(x) + (x - x.mean())**2 / np.sum((x - x.mean())**2))
    y_err = x.std()

    fig, ax = plt.subplots()
    ax.plot(x, y_est, '-')
    ax.fill_between(x, y_est - y_err, y_est + y_err, alpha=0.2, color='red')
    ax.plot(x, y, 'o', color='black', markersize=2)

    plt.xlabel('Time (day)')
    plt.ylabel('Number of Crews')
    # plt.legend((ax2, ax), ('Inside Crews', 'Outside Crews'))
    plt.xlim((0, 1.2))
    # plt.ylim((0, 500))
    plt.show()


def plot_supply_critical_concept(f):

    cost = []
    tmax = []
    with open(f, 'r') as csvf:
        reader = csv.reader(csvf)
        headers = next(reader, None)
        for row in reader:
            cost.append(int(row[1])/1000)
            tmax.append(int(row[2]))

    i, j, m = 0, 0, 0

    fig = plt.gca()
    v, w = [], []

    for k in range(1, len(cost)):
        if cost[k] == 0:
            x = cost[i:k]
            x.append(200)
            y = tmax[i:k]
            y.append(tmax[k-1])
            v.append(sum([t for t in x])/(k - i))
            w.append(sum([t for t in y])/(k - i))
            i = k
            j += 1
            if j < 86:
                plt.plot(x, y, color='lightgray', linewidth=1)
            else:

                while y[-m-1] == y[-m-2]:
                    m += 1

                plt.plot(x, y, color='black', linestyle='dashed', linewidth=3)
                plt.plot(x[-m-1], y[-1], marker='o', markerfacecolor='None', color='red', markersize=15)
                # plt.annotate('Maximum Effective Investment', xy=(x[-m-1], y[-1]), xytext=(x[-m-1] - 5, y[-1] + 100),
                #     arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6), size=12,
                #     )

                break

    print(sum([x for x in v])/len(v), sum([x for x in w])/len(w))
    plt.xlim((0, 20))
    plt.ylim((0, 400))
    plt.xlabel('Required Budget (million dollars)')
    plt.ylabel('Restoration Time (days)')
    formatter = ticker.FormatStrFormatter('$%1.0fM')
    fig.xaxis.set_major_formatter(formatter)
    plt.show()


def plot_supply_boxplot(f):

    results = []
    with open(f, 'r') as csvf:
        reader = csv.reader(csvf)
        headers = next(reader, None)
        for row in reader:
            results.append([int(x) for x in row])

    [dmg, cost, tmax, hv_sub_av, lv_sub_av, hv_tran_av, lv_tran_av, hv_sub_dmg, lv_sub_dmg,
     hv_tran_dmg, lv_tran_dmg] = [*zip(*results)]

    f, (ax1, ax2) = plt.subplots(1, 2, sharey=False)

    # 1- damage
    ax1.boxplot(dmg)
    ax1.set_title('damage')

    # 1- cost
    ax2.boxplot(cost)
    ax2.set_title('budget')

    plt.show()


    exit()

    i, j, m = 0, 0, 0

    fig = plt.gca()
    for k in range(1, len(cost)):
        if cost[k] == 0:
            x = cost[i:k]
            x.append(200)
            y = tmax[i:k]
            y.append(tmax[k-1])
            i = k
            j += 1
            if j < 85:
                plt.plot(x, y, color='lightgray', linewidth=1)
            else:

                while y[-m-1] == y[-m-2]:
                    m += 1

                plt.plot(x, y, color='black', linestyle='dashed', linewidth=3)
                plt.plot(x[-m-1], y[-1], marker='o', color='red', markersize=12)
                plt.annotate('Critical Point', xy=(x[-m-1], y[-1]), xytext=(x[-m-1] + 30, y[-1] + 100),
                    arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6), size=12,
                    )

                break
    plt.xlim((-5, 200))
    plt.ylim((0, 400))
    plt.xlabel('Required Budget (million dollars)')
    plt.ylabel('Recovery Time (day)')
    formatter = ticker.FormatStrFormatter('$%1.0fM')
    fig.xaxis.set_major_formatter(formatter)
    plt.show()


def main():
    # network_in_recovery_process(E, title)
    pass

if __name__ == '__main__':

    main()


















