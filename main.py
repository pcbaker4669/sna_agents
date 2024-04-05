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
# allow an initial network, strongly connected, with everyone having an
# in-degree of one.  The tot_nodes is set to 5 (initially) and will be increased.
# The produced networks will be viewed in Gephi (network analysis software) to observe
# proper construction of a scale-free graph.  Before I add other selection
# metrics, I would like to see the formation of a Barabási–Albert (BA)
# scale-free network model

# Updates
# Noticed that a new_node can select itself for a parent, removing this
# possibility
# The scale free network is not forming correctly for high degree nodes,
# there is still a scale-free structure, but graphs of 6000 nodes should have
# a few nodes with 100's of in-degree.  Continuing


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
# prob = (original_prob * weight_for_original_prob) +
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

# Objective 5: When the network is created, add one more metric which is
# interation score.  0 is when no-one even looks at the video (the lowest score),
# 10 would be like, share, watch all, comment.  Create network using the interaction
# score with the in-degree and similarity, randomly assign the interaction score
# on creation and use it in the
# get_best_match function to find the match.  We will pass in the weights for
# in-degree, word-similarity, and the interaction score (weight = (.3, .3, .34)).
# The interaction score will be normalized much like the degree where the node's
# interaction score will be divided by the total of all interactions in the graph
# The resulting network is still a scale-free network with little change to the
# overall structure.

# Objective 6 (4/3/2024): create an updating graph that can "run" updates.  For the
# sake of reducing complexity, no new nodes will be added to the graph
# while we run update.  Implementing a visualization mechanism to see how in-degree
# distribution changes for the updates.  Currently, when running the graph, the network
# increases nodes with large in-degree.  How will this change with increasing the weight
# on word similarity?

import networkx as nx
import agent as ag
import chart
import random

start_node_num = 4
tot_nodes = 100
fileNumber = 1
export_edge_table_flag = True
export_graph_metrics_flag = False
weights = [.3, .4, .3]


def export_graph():
    edges = g.edges
    f_ref = open(f"tot_node{tot_nodes}_{fileNumber}.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


def export_graph_metrics():
    f_ref = open(f"Metrics{tot_nodes}_{fileNumber}.csv", "w")
    s = ("{}, {}, {}, {}, {}, {}, {}, {}\n"
         .format("Id", "In-Degree", "Out-Degree", "Degree",
                 "Eccentricity", "PageRank", "Word-Metric", "Interaction-Score"))
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

        s = ("{}, {}, {}, {}, {}, {:.5f}, {}, {}\n".
             format(node.get_name(), in_deg, out_deg, deg,
                    ecc[k], page_rank[k], sna_model.get_nodes()[k].get_word_metric(),
                    sna_model.get_nodes()[k].get_interaction_score()))
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
    best_match = sna_model.get_best_match(new_node)
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
# it takes a number of edges to modify in the network, randomly picks that many
# edges.  For each edge selected, get the source node, remove the edge from the graph,
# find a new node for the source node to point to
def modify_graph(num_of_edges):
    edge_lst = []
    edges_from_graph = list(g.edges)
    # randomly select 5 edges from the graph
    while len(edge_lst) <= num_of_edges:
        e = random.choice(edges_from_graph)
        edge_lst.append(e)
    # for each selected edge, get the source node, remove the edge
    for e in edge_lst:
        source_node = sna_model.get_nodes()[e[0]]
        old_target_node = sna_model.get_nodes()[e[1]]
        # remove the old edge, this has be making our graph disconnected so comment
        # out the "remove edge" for now
        # g.remove_edge(*e)
        # find a new match, now we are using interaction scores
        new_match = sna_model.get_best_match(source_node, weights)
        g.add_edge(source_node.get_name(), new_match.get_name())
        degree_in = g.in_degree(source_node.get_name())
        source_node.set_in_degree(degree_in)
        degree_in = g.in_degree(old_target_node.get_name())
        old_target_node.set_in_degree(degree_in)
        degree_in = g.in_degree(new_match.get_name())
        new_match.set_in_degree(degree_in)
        sna_model.update_graph_totals()



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

if export_edge_table_flag:
    export_graph()

h = chart.Histo()

for i in range(400):
    modify_graph(5)
    data = sna_model.get_in_degree_lst()
    h.update_plot(data, .05)
    fileNumber = i + 1
    if export_graph_metrics_flag:
        export_graph_metrics()
