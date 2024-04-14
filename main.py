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
import graph

start_node_num = 5
tot_nodes = 100
fileNumber = 1
export_edge_table_flag = True
export_graph_metrics_flag = False

in_degree_wt = .5
similarity_wt = .5


def export_graph():
    edges = g.edges
    f_ref = open(f"tot_node{tot_nodes}_{fileNumber}.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


def export_graph_metrics():
    f_ref = open(f"Metrics{tot_nodes}_{fileNumber}.csv", "w")
    s = ("{}, {}, {}, {}, {}, {}\n"
         .format("Id", "In-Degree", "Out-Degree", "Degree",
                 "Mod Class", "Word-Metric"))
    f_ref.write(s)
    nodes = sna_model.get_nodes()
    keys = nodes.keys()

    for k in keys:
        node = nodes[k]
        in_deg = g.in_degree(node.get_name())
        out_deg = g.out_degree(node.get_name())
        deg = g.degree(node.get_name())

        s = ("{}, {}, {}, {}, {}, {}\n".
             format(node.get_name(), in_deg, out_deg, deg, 0,
                    sna_model.get_nodes()[k].get_word_metric()))
        f_ref.write(s)

    f_ref.close()


# Create start_node_num, initially 4, each node is pointing to
# the next node in a loop to ensure the graph is connected and
# all four initial nodes have an in-degree
def setup():
    n = []
    mean = random.uniform(.2, .8)
    sig = random.uniform(.1, .4)
    for idx in range(0, start_node_num):
        n.append(sna_model.create_start_node(mean, sig))
        g.add_node(n[idx].get_name())
    for i in range(1, start_node_num):
        g.add_edge(n[i - 1].get_name(), n[i].get_name())
    g.add_edge(n[start_node_num - 1].get_name(), n[0].get_name())
    my_graph.display_graph()
    my_graph.freeze_plot()
    for i in range(0, start_node_num):
        degree_in = g.in_degree(n[i].get_name())
        n[i].set_in_degree(degree_in)
    sna_model.update_graph_totals()
    print("nodes from setup = ", len(n))
    return n


# This function is used in the initial build of the network
# it creates set of nodes, finds a parent based strictly on similarity, and
# finds a child node based on in-degree and similarity
def add_nodes_to_graph(last_set):
    this_set = []
    # get node from last_set and add some recommendations
    for node in last_set:
        new_node = sna_model.create_rnd_node()
        this_set.append(new_node)
        g.add_node(new_node.get_name())

        # find recommended nodes the new node will point to first before
        # we find a parent.
        best_match = sna_model.get_good_match(new_node, in_degree_wt,
                                              similarity_wt)
        g.add_edge(best_match.get_name(), new_node.get_name())
        bm_in_degree = g.in_degree(best_match.get_name())
        nn_in_degree = g.in_degree(new_node.get_name())
        best_match.set_in_degree(bm_in_degree)
        new_node.set_in_degree(nn_in_degree)
        sna_model.update_graph_totals()
    my_graph.display_graph()
    my_graph.freeze_plot()
    return this_set


def go(last_set):
    nodes_to_add = tot_nodes - len(last_set)
    nodes_added = sna_model.get_count()
    print("node count is = ", nodes_added)
    while nodes_added < nodes_to_add:
        last_set = add_nodes_to_graph(last_set)
        nodes_added = sna_model.get_count()
        print("node count is = ", nodes_added)
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

print("4. Weight of in-degree (.5 default)")
try:
    in_degree_wt = float(input())
except ValueError:
    print("in-degree default to .5")
    in_degree_wt = .5

print("5. Weight of similarity (.5 default)")
try:
    similarity_wt = float(input())
except ValueError:
    print("similarity default to .5")
    similarity_wt = .5

g = nx.DiGraph()
sna_model = ag.SNA_Model(100000)
my_graph = graph.GraphNet(g)
last_set_of_nodes = setup()
go(last_set_of_nodes)

# if export_edge_table_flag:
#     export_graph()

h = None
# if do_run_modifications > 0:
#     h = chart.Histo()

original_list = sna_model.get_in_degree_lst()[:]

in_degree_data_org = sna_model.get_in_degree_lst()

print("end network = ", sna_model.get_in_degree_lst())
if export_edge_table_flag:
    export_graph()

# if do_run_modifications == 0:
#     h = chart.Histo()
# h.final_plot(in_degree_data_org)
