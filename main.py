# Goal
# Primary Objective: To model a social network recommendation
# system similar to YouTube where network structure is a hybrid
# scale-free network.
# Objective 1: 3_23_2024 - Create a free scale network
# where choices for recommended nodes are based on a node's interaction score,
# the interaction score is only based on in-degree. But we will want to
# add a similarity score also.  Additionally, a user interaction score would
# be desirable which would mimic users doing: view, click, share, comment,
# and watch time.

# Testing will start with only 5 nodes.  The start_node_num is set to 4 to
# allow an initial networks with everyone having an in-degree of one.
# tot_nodes is set to 5 (initially) and will be increased.  The produced
# networks will be view in Gephi (network anaylsis software) to observe
# proper construction of a scale-free graph.  Before I add other selection
# metrics, I would like to see the formation of a Barabási–Albert (BA)
# scale-free network model

# Updates
# Noticed that a new_node can select itself for a parent, removing this
# possibility

# Objective 2: 3/24/2024
# Lets modify the selection process so that a similarity score
# will play into account for at least the parent node.  Lets find
# the best match for the parent

# Correction 1: 3/28/2024
# Noticed a lack of preferred attachment with large networks.  The problem
# with the preferred attachment probability is I didn't account for
# the probability of attachment to get so low. When converting to percent,
# I inadvertantly rounded so that everything under 1% had the same probability
# of attachment.  This showed in the data for the 12K and 22K networks significantly.
# correcting the problem

# Objective 3: 3/28/2024 (not done yet)
# Previously, the model matched the best parent with the created node
# based on word_metric similarity.  But nodes should also be "selected" based
# on similarity, as well as interactions (currently only in-degree for interactions).
# Pass the node created into the get_popular_match and calculate an attachment
# probability based on similarity score and interaction (get_node_att_prob)
# use weighting so that one score doesn't crush the other score
# weight_for_original_prob = 0.5
# weight_for_similarity_score = 0.5
# weighted_prob = (original_prob * weight_for_original_prob) +
#                      (similarity_score * weight_for_similarity_score)
#
#

# Objective 4: The similarity probability selection needs to be adjusted because
# it is too high and squashes the interaction probability.  Decided to use the
# following calculation for similarity probability:  (1 - abs(score1 - score2))/self.tot_word_metric
# this will place the selection probability on the same order of magnitude as
# the in-degree probability.  We can then multiply the probabilities when making
# a selection and have roughly equal weight. The result is a scale-free network
# which is very close to the original.

# Objective 5: create a continual updating graph that can "run", we will have
# and interaction score.  When the network is created, query the user on
# a word metric they would like to search on.  Find the node with the word metric
# score or the next higher.  Return a list of nodes searched on the surrounding
# the word metric.  We will query the user for a rating (interaction score), 0
# is not even looked at, 10 would be like, share, watch all, comment.  Restructure
# the graph based on the new interaction score

import networkx as nx
import agent as ag
import random as rnd
import scipy

start_node_num = 4
tot_nodes = 100
fileNumber = 1
export_edge_table_flag = True
export_graph_metrics_flag = False


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
    for k in keys:
        node = nodes[k]
        in_deg = g.in_degree(node.get_name())
        out_deg = g.out_degree(node.get_name())
        deg = g.degree(node.get_name())
        ecc = dict(nx.eccentricity(g, v=[k]))

        components = []
        str_comp = []
        modularity = []
        c_c = []
        eigen_cent = []
        s = ("{}, {}, {}, {}, {}, {:.5f}, {}\n".
             format(node.get_name(), in_deg, out_deg, deg,
                    ecc[k], page_rank[k], sna_model.get_nodes()[k].get_word_metric()))
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
        # print("initialized node: Name: {}, Interaction: {}"
        #       .format(i, n[i].get_in_degree()))


def add_node_to_graph():
    # the new node is created and added to the graph, additionally
    # the sna_model adds the node to the dictionary of nodes
    new_node = sna_model.create_rnd_node()
    g.add_node(new_node.get_name())

    # find recommended nodes the new node will point to first before
    # we find a parent.
    best_match = sna_model.get_structural_match(new_node)
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
    # print("(add_node_to_graph): new node: {}, parent: {}, rec: {} denominator: {:.3f}".
    #       format(new_node.get_name(), parent_match.get_name(),
    #              best_match.get_name(),
    #              sna_model.get_node_att_prob(new_node)))


def go():
    adds_to_add = tot_nodes - start_node_num
    for i in range(adds_to_add):
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


g = nx.DiGraph()
sna_model = ag.SNA_Model()

setup()
go()


node_lst = sna_model.get_nodes_sorted_by_metric()

print('What would you like to search on? (Enter:0-100 or quit: -1')
response = int(input())
while response >= 0:
    matches = []
    idx = response
    r_idx = response-1
    for i in range(len(node_lst)):
        n = node_lst[i]
        if n.get_word_metric() >= response or i == len(node_lst)-1:
            matches.append(n)
            if i+1 < len(node_lst):
                matches.append(node_lst[i+1])
            if i-1 >= 0:
                matches.append(node_lst[i-1])
            if i-2 >= 0:
                matches.append(node_lst[i-2])
            break
    for n in matches:
        print("=> ", n)
    print('What would you like to search on? (Enter:0-100 or quit: -1')
    response = int(input())







if export_edge_table_flag:
    export_graph()

if export_graph_metrics_flag:
    export_graph_metrics()
