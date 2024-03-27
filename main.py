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

# Objective 3: 3/26/2024
# Previously, the model matched the best parent with the created node
# based on similarity.  But nodes should also be "selected" based
# on similarity, as well as interactions (currently only in-degree for interactions).
# Pass the node created into the get_popular_match and calculate an attachment
# probability based on similarity score and interaction (get_node_att_prob)
# use weighting so that one score doesn't crush the other score
# weight_for_original_prob = 0.5
# weight_for_similarity_score = 0.5
# weighted_prob = (original_prob * weight_for_original_prob) +
#                      (similarity_score * weight_for_similarity_score)
#

import networkx as nx
import agent as ag
import random as rnd
start_node_num = 4
tot_nodes = 22000
fileNumber = 1


def export_graph():
    edges = g.edges
    f_ref = open(f"tot_node{tot_nodes}_{fileNumber}.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


g = nx.DiGraph()
sna_model = ag.SNA_Model()


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
    g.add_edge(n[start_node_num-1].get_name(), n[0].get_name())

    for i in range(0, start_node_num):
        degree_in = g.in_degree(n[i].get_name())
        n[i].set_in_degree(degree_in)
        sna_model.update_graph_totals()
        print("initialized node: Name: {}, Interaction: {}"
              .format(i, n[i].get_in_degree()))


def add_node_to_graph():
    # the new node is created and added to the graph, additionally
    # the sna_model adds the node to the dictionary of nodes
    new_node = sna_model.create_rnd_node()
    g.add_node(new_node.get_name())

    # find recommended nodes the new node will point to first before
    # we find a parent.
    best_match = sna_model.get_popular_match()
    g.add_edge(new_node.get_name(), best_match.get_name())
    print("best match for new node {} is {}"
          .format(new_node.get_name(), best_match.get_name()))

    # find the parent in the graph so then new node gets a chance. The
    # parent selection will need a matching criteria, but currently it's
    # a random draw
    parent_match = sna_model.get_parent_for_new_node(new_node)
    g.add_edge(parent_match.get_name(), new_node.get_name())
    print("the parent selected for new node {} is {} (by chance) "
          .format(new_node.get_name(),  parent_match.get_name()))

    # update interaction for new_node (in-degree) and best_match
    # (graph in-degree), parent_match will not get updated because it's
    # out-degree
    best_match.increment_in_degree()
    new_node.increment_in_degree()
    sna_model.update_graph_totals()
    print("(add_node_to_graph): new node: {}, parent: {}, rec: {} denominator: {:.3f}".
          format(new_node.get_name(), parent_match.get_name(),
                 best_match.get_name(),
                 sna_model.get_node_att_prob(new_node)))


def go():
    adds_to_add = tot_nodes - start_node_num
    for i in range(adds_to_add):
        add_node_to_graph()

setup()
go()
print("A list of nodes in sna_model with there interaction scores: ",sna_model)
export_graph()
