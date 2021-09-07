"""QuickGraph Library (v0.1)
by Mobile Systems and Networking Group @ Fudan University
Contact: gongqingyuan AT fudan.edu.cn
"""

from igraph import *
import leidenalg
import statistics
import random
import community as community_louvain
import networkx.algorithms.community as nx_comm
import matplotlib.pyplot as plt
import numpy as np
import pathlib
import timeit
import math

def info(G):
    """
    This function will show some basic properties of graph G, including:
        average degree,
        average clustering coefficient,
        number of connected components,
        percentage of nodes within the largest connected component (LCC),
        modularity value of the graph using the louvain partition,
        CDF plot of degree and clustering coefficient,
        BAR plot of up to top 10 large connected components.
        All figures will be saved in a new ./figures/ folder, with number of nodes and edges entitled.
    """
    start = timeit.default_timer()
    num_nodes = G.vcount()
    print("Number of Nodes:", num_nodes, end=", ")
    num_edges = G.ecount()
    print("Number of Edges:", num_edges)

    degree_all = 0
    degree_ytick = []
    for uid in G.vs.indices:
        degree_all += G.degree(uid)
        degree_ytick.append(G.degree(uid))
    average_degree = round(degree_all/num_nodes, 4)       
    print("Avg. degree:", average_degree, end=", ")
    plot_CDF(degree_ytick, 'Degree', num_nodes, num_edges)
    node_local_cc = G.transitivity_local_undirected()
    cc_sum = 0
    for cc_i in range(len(node_local_cc)):
        if math.isnan(node_local_cc[cc_i]):
            continue
        cc_sum += node_local_cc[cc_i]
    print("Avg. clustering coefficient:", round(cc_sum/num_nodes, 4))
    #print("Avg. clustering coefficient:", round(mean(G.transitivity_local_undirected()), 4), end=", ")
    #clustering = list(nx.clustering(G).values())
    #plot_CDF(clustering, "ClusteringCoefficient", num_nodes, num_edges)
    
    leidenalg_part = leidenalg.find_partition(G, leidenalg.ModularityVertexPartition)
    print("Modularity (Leidenalg):", round(G.modularity(leidenalg_part), 4), end=", ")
    label_part = G.community_label_propagation()
    print("Modularity (Label_Propagation):", round(G.modularity(label_part), 4))
    cc_all = G.clusters()
    num_nodes_LCC = cc_all.giant().vcount()
    print("Number of connected components:", len(cc_all), end=", ")
    print("Number of nodes in LCC:", num_nodes_LCC, "(",round(num_nodes_LCC/num_nodes*100, 4),"%)")

    connected_component_size = []
    for i in range(len(cc_all)):
        connected_component_size.append(len(cc_all[i]))
    
    cc = sorted(connected_component_size, reverse=True)
    if len(cc)  > 0:
        data = []
        counter = 0
        while counter < min(len(cc), 10):
            data.append(cc[counter])
            counter += 1
        plot_BAR(list(data), num_nodes, num_edges)
    stop = timeit.default_timer()
    print("Time (G_info):", stop-start)      

        
def plot_CDF(data, index, num_nodes, num_edges):
    plot_xtick = sorted(data)
    plot_ytick = np.array(data)
    xrange = np.percentile(plot_ytick,95)

    pdf = plot_ytick/sum(plot_ytick)
    cdf = np.cumsum(pdf)
    plt.plot(plot_xtick, cdf, label = 'CDF')
    plt.xlabel(index)
    plt.ylabel('Fraction')
    plt.title('CDF of '+index)
    
    plt.xlim([0,max(xrange, 0.00001)])
    plt.ylim([0,1])
    fig_name = 'QuickGraph_N' + str(num_nodes) + '_E' + str(num_edges) + '_' +index +'_CDF'
    pathlib.Path('./figures').mkdir(parents=True, exist_ok=True) # Python 3.5 and above
    plt.savefig('./figures/'+fig_name+'.eps', bbox_inches='tight')
    plt.close()

def plot_BAR(data, num_nodes, num_edges):
    plt.style.use('ggplot')

    x_ticks = []
    counter = 0
    while counter < len(data):
        counter += 1
        x_ticks.append(counter)

    y = data

    plt.bar(x_ticks, y, log=True)
    plt.xticks(x_ticks)
    plt.xlabel("Top 10 Connected Components")
    plt.ylabel("Size")
    plt.title("Sizes of the top 10 connected components")
    fig_name = 'QuickGraph_N' + str(num_nodes) + '_E' + str(num_edges) + '_'  +'_BAR'
    plt.savefig('./figures/'+fig_name+'.png', bbox_inches='tight')
    plt.close()

def LCC_analysis(G):

    """
    This function will show some basic properties about the largest connected component (LCC), including:
        average degree of the LCC,
        average clustering coefficient of the LCC,
        modularity value of the LCC using the louvain partition,
        (rough) distribution of shortest path lengths using 500 randomly selected node pairs in the LCC.

    """
    start = timeit.default_timer()
    largest_cc = G.clusters().giant()
    cc_nodes = largest_cc.vs.indices
    nodes_num = largest_cc.vcount()
    LCC_degrees = largest_cc.degree()
    LCC_degrees_seq = []
    for uid in cc_nodes:
        LCC_degrees_seq.append(LCC_degrees[uid])
        
    sum_degree = 0
    for x in LCC_degrees:
        sum_degree += x
    print("LCC: Avg. degree =", round(sum_degree/nodes_num, 4),end=", ")

    print("Avg. clustering coefficient =", round(largest_cc.transitivity_undirected(), 4),end=", ")
    
    leidenalg_part = leidenalg.find_partition(largest_cc, leidenalg.ModularityVertexPartition)
    print("Modularity (Leidenalg):", round(largest_cc.modularity(leidenalg_part),4), end=", ")
    label_part = largest_cc.community_label_propagation()
    print("Modularity (Label_Propagation):", round(largest_cc.modularity(label_part),4))

    shortest_path_pdf = {}
    shortest_path_mean = []
    list_path_length = []
    for counter in range(500):
        source = cc_nodes[random.randint(0,nodes_num-1)]
        dest = cc_nodes[random.randint(0,nodes_num-1)]
        shortest_path_length = largest_cc.shortest_paths(source, dest)
        if shortest_path_length[0][0] in shortest_path_pdf.keys():
            shortest_path_pdf[shortest_path_length[0][0]] += 1
            shortest_path_mean.append(shortest_path_length[0][0])
        else:
            shortest_path_pdf[shortest_path_length[0][0]] =1
            shortest_path_mean.append(shortest_path_length[0][0])
    
    list_path_length = list(shortest_path_pdf.keys())
    list_path_length.sort()
    print("(rough) shortest path length =", end = " ")
    for index in list_path_length: 
        print(index,":",shortest_path_pdf[index], "(",shortest_path_pdf[index]/10, "%)",end = ", ")

    print("Avg. shortest path length =",statistics.mean(shortest_path_mean))
    stop = timeit.default_timer()
    print("Time (LCC):", stop-start)      

def demo():
    G = Graph()
    with open('./nodes_16007.csv', 'r',newline='') as f:
        reader = f.readline()
        nodes = []
        while reader:
            nodes.append(int(reader))
            reader = f.readline()
        G.add_vertices(nodes)

    with open('links_16007.csv', 'r', newline='') as f: #Add edges into G
        reader = f.readline()
        edges = []
        while reader:
            x = reader.split(',')
            node_1 = int(x[0])
            node_2 = int(x[1])
            edges.append((node_1, node_2))
            reader = f.readline()
        G.add_edges(edges)
    
    


