# Primary Objective: To model a social network recommendation
# system similar to YouTube where network structure is a hybrid
# scale-free network.
# Summary: To create an agent-based model for social network community analysis using
# YouTube data as a reference.

# The model will be based on empirical data collected by scraping YouTube data.
# First, we go to a creator’s video list, collect the featured videos, and collect
# the videos recommended based on the selection of the video.  There is a theme to
# the recommendations that contributes and predicts the formation of communities in
# the network.  Recreating the community formation is the objective of the model.

# Each YouTube scrape per creator is placed into Gephi network analysis tool and
# community partitioning is run using the modularity package.  Subsequent scrapes
# consist of taken three randomly chosen videos in separate communities and finding
# that creators page and repeating the scrape.  Chaining the scrapes from a video that
# is in the original set ensures that the sample network will be complete but allows us
# to branch out and increase our sample data.

# It should be possible to create an agent-based model that forms the hybrid scale-free
# network similar to YouTube and creates communities of similar size and structure with
# a small number of parameters.  Agents will maintain information about similarity which
# will be the driver for community formation.  The network will be created based on node
# selection of “in-degree”, as well as matching similarity.  Initially, interaction
# scores were added but have been discarded as community formation is now the objective.
# Once the network is created, runs will be performed that allows nodes to find better
# matching on similarity.  Nodes will select other nodes at random and connect to better
# nodes.

# Currently, similarity is based on a single score which represents a value that
# has been obtained by some work pattern matching algorithm.  Initially, I used integers
# from 0-99 and randomly assigned nodes a word metric score. However, having a discrete
# value does not scale well.  The similarity score (word-metric) will be real numbers
# from 0-1 and categories have more flexibility for growth.


import networkx as nx
import agent as ag
import chart
import random
import scipy

start_node_num = 4
tot_nodes = 100
fileNumber = 1
export_edge_table_flag = True
export_graph_metrics_flag = False
do_run_modifications = False
num_of_run_modifications = 10
in_degree_wt = .33
similarity_wt = .33


def export_graph():
    edges = g.edges
    f_ref = open(f"tot_node{tot_nodes}_{fileNumber}.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


def export_graph_metrics():
    f_ref = open(f"Metrics{tot_nodes}_{fileNumber}.csv", "w")
    s = ("{}, {}, {}, {}, {}, {}, {}\n"
         .format("Id", "In-Degree", "Out-Degree", "Degree",
                 "Eccentricity", "PageRank", "Word-Metric"))
    f_ref.write(s)
    nodes = sna_model.get_nodes()
    keys = nodes.keys()
    page_rank = dict(nx.pagerank(g))
    ecc = {}
    try:
        ecc = dict(nx.eccentricity(g))
    except nx.NetworkXException:
        print("eccentricity error!!")
    for k in keys:
        node = nodes[k]
        in_deg = g.in_degree(node.get_name())
        out_deg = g.out_degree(node.get_name())
        deg = g.degree(node.get_name())

        s = ("{}, {}, {}, {}, {}, {:.8f}, {}\n".
             format(node.get_name(), in_deg, out_deg, deg, ecc[k],
                    page_rank[k], sna_model.get_nodes()[k].get_word_metric()))
        f_ref.write(s)

    f_ref.close()


# Create start_node_num, initially 4, each node is pointing to
# the next node in a loop to ensure the graph is connected and
# all four initial nodes have an in-degree
def setup():
    n = []
    for i in range(0, start_node_num):
        n.append(sna_model.create_rnd_node())
        g.add_node(n[i].get_name())

    for i in range(1, start_node_num):
        g.add_edge(n[i - 1].get_name(), n[i].get_name())
    g.add_edge(n[start_node_num - 1].get_name(), n[0].get_name())

    for i in range(0, start_node_num):
        degree_in = g.in_degree(n[i].get_name())
        n[i].set_in_degree(degree_in)
        sna_model.update_graph_totals()


# This function is used in the initial build of the network
# it creates a node, finds a parent based strictly on similarity, and
# finds a child node based on in-degree and similarity
def add_node_to_graph():
    # the new node is created and added to the graph, additionally
    # the sna_model adds the node to the dictionary of nodes
    new_node = sna_model.create_rnd_node()
    g.add_node(new_node.get_name())

    # find recommended nodes the new node will point to first before
    # we find a parent.
    best_match = sna_model.get_good_match(new_node, in_degree_wt,
                                          similarity_wt)
    g.add_edge(new_node.get_name(), best_match.get_name())
    # print("best match for new node {} is {}"
    #       .format(new_node.get_name(), best_match.get_name()))

    # find the parent in the graph so then new node gets a chance. The
    # parent selection will need a matching criteria, but currently it's
    # a random draw
    parent_match = sna_model.get_parent_for_new_node(new_node)
    g.add_edge(parent_match.get_name(), new_node.get_name())
    # print("the parent selected for new node {} is {} (by chance) "
    #       .format(new_node.get_name(),  parent_match.get_name()))

    # update interaction for new_node (in-degree) and best_match
    # (graph in-degree), parent_match will not get updated because it's
    # out-degree
    best_match.increment_in_degree()
    new_node.increment_in_degree()
    sna_model.update_graph_totals()


# This function is used to update the network
# it takes a number of edges to modify in the network, randomly picks number of
# edges from "num_of_edges".  For each edge selected, get the source node, and it's
# target node, pick a new node, if the similarity score and interaction score is
# higher than the old target, remove the edge from the graph is if it doesn't cause
# a disconnected graph, and add edge to the new target.
# find a new node for the source node to point to
def modify_graph(num_of_nodes):
    all_nodes = sna_model.get_nodes()
    keys = list(all_nodes.keys())
    node_mod_cnt = 0
    while node_mod_cnt < num_of_nodes:
        node_mod_cnt += 1
        k = random.choice(keys)
        source_node = all_nodes[k]
        print("node to change", source_node.get_name(), ", out deg: ", g.out_degree(source_node.get_name()))
        # get worst match of source node
        edges = g.out_edges([source_node.get_name()])
        print("edges in node to change = ", edges)
        lst_to_check = []
        for e in edges:
            lst_to_check.append(all_nodes[e[1]])

        old_target_node = sna_model.get_least_sim_from_lst(source_node, lst_to_check)
        new_match = sna_model.get_better_match(source_node, old_target_node,
                                                   in_degree_wt, similarity_wt)

        src_out_degree = g.out_degree(source_node.get_name())
        # if old_target_node has out-degree > 1 it's okay to remove
        old_tgt_in_degree = g.in_degree(old_target_node.get_name())
        if src_out_degree > 1 and old_tgt_in_degree > 1:
            g.remove_edge(source_node.get_name(), old_target_node.get_name())

        # attach a new match
        g.add_edge(source_node.get_name(), new_match.get_name())

        old_tgt_degree_in = g.in_degree(old_target_node.get_name())
        old_target_node.set_in_degree(old_tgt_degree_in)
        new_match_degree_in = g.in_degree(new_match.get_name())
        new_match.set_in_degree(new_match_degree_in)
        sna_model.update_graph_totals()


def go():
    nodes_to_add = tot_nodes - start_node_num
    for i in range(nodes_to_add):
        add_node_to_graph()
        if i % 100 == 0:
            print("node = ", i)
    print("network created, time to click on something")


print("*************************************************")
print("************* Welcome to SNA Model **************")
print("1. Enter the number of node in the network:")
tot_nodes = int(input())
print("2. Would you like to export the edge list? (t or f)")
export_edges = input()
if export_edges == 't':
    export_edge_table_flag = True
else:
    export_edge_table_flag = False
print("3. Would you like to export the network metrics? (t or f)")
export_metrics = input()
if export_metrics == 't':
    export_graph_metrics_flag = True
else:
    export_graph_metrics_flag = False
print("4. Do run modifications? (0 is no, > 0 is the number of runs)")
do_run_modifications = int(input())
print("5. Weight of in-degree (.5 default)")
try:
    in_degree_wt = float(input())
except ValueError:
    print("in-degree default to .5")
    in_degree_wt = .5

print("6. Weight of similarity (.5 default)")
try:
    similarity_wt = float(input())
except ValueError:
    print("similarity default to .5")
    similarity_wt = .5

g = nx.DiGraph()
sna_model = ag.SNA_Model()

setup()
go()

# if export_edge_table_flag:
#     export_graph()

h = None
if do_run_modifications > 0:
    h = chart.Histo()

original_list = sna_model.get_in_degree_lst()[:]
edge_changes_per_update = tot_nodes * .05

for i in range(do_run_modifications):
    modify_graph(edge_changes_per_update)
    in_degree_data = sna_model.get_in_degree_lst()
    print("i = ", i)
    h.update_plot(in_degree_data)
    fileNumber = i + 1
    if export_graph_metrics_flag:
        export_graph_metrics()
if do_run_modifications == 0:
    if export_graph_metrics_flag:
        export_graph_metrics()
print("start network = ", original_list)
print("end network = ", sna_model.get_in_degree_lst())
if export_edge_table_flag:
    export_graph()

if do_run_modifications == 0:
    h = chart.Histo()
h.final_plot(sna_model.get_in_degree_lst())
