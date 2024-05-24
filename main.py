# Primary Objective: To model a social network recommendation
# system similar to YouTube where network structure is a hybrid
# scale-free network.
# Summary: To create an agent-based model for social network community analysis using
# YouTube data as a reference.

import networkx as nx
import numpy as np

import agent as ag
import random
# originally 123
random.seed(123)

start_node_num = 4
tot_nodes = 100
fileNumber = 1
export_edge_table_flag = True
export_graph_metrics_flag = False
do_run_modifications = False
do_att_prob_logging = False
num_of_run_modifications = 10
in_degree_wt = .33
similarity_wt = .33
removals = 0
new_nodes_skipped = 0
edge_adds = 0
old_tgt_skipped = 0
tot_mods = 0


def export_graph(prefix):
    edges = g.edges
    f_ref = open(f"{prefix}_EdgeTbl_{tot_nodes}_SeleM_{selection_mult}_{fileNumber}.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


def export_graph_metrics():
    f_ref = open(f"M{tot_nodes}_R{fileNumber}_SeleM_{selection_mult}.csv", "w")
    s = ("{}, {}, {}, {}, {}, {}\n"
         .format("Id", "In-Degree", "Out-Degree", "Degree",
                 "Community Group", "Word-Metric"))
    f_ref.write(s)
    nodes = sna_model.get_nodes()
    keys = nodes.keys()

    for k in keys:
        node = nodes[k]
        in_deg = g.in_degree(node.get_name())
        out_deg = g.out_degree(node.get_name())
        deg = g.degree(node.get_name())
        mod = node.get_community()
        s = ("{}, {}, {}, {}, {}, {:.5f}\n".
             format(node.get_name(), in_deg, out_deg, deg, mod,
                    sna_model.get_nodes()[k].get_word_metric()))
        f_ref.write(s)

    f_ref.close()


def export_run_data():
    data = sna_model.get_mean_std_dev_of_com_by_run()
    f_ref = open(f"Comm_{tot_nodes}_R{fileNumber}_SeleM_{selection_mult}.csv", "w")
    f_ref.write("Run, Std Dev\n")
    run_count = 0

    for d in data:
        f_ref.write("{}, {:.5f}\n".format(run_count, d))
        run_count += 1
    f_ref.close()

    data = sna_model.get_community_run_metrics_for_each_all_groups()
    f_ref = open(f"CG_{tot_nodes}_R{fileNumber}_SeleM_{selection_mult}.csv", "w")
    f_ref.write("Community, Count, Mean, Std Dev\n")

    for d in data:
        f_ref.write(d)
    f_ref.close()

    # attachment probabilities
    if do_att_prob_logging:
        deg_att_data = sna_model.get_in_degree_att_probs_log()
        sim_att_data = sna_model.get_wm_sim_att_probs_log()
        print("size of att_data = ", len(deg_att_data))
        f_ref = open(f"Probability_{tot_nodes}_R{fileNumber}_SeleM_{selection_mult}.csv", "w")
        f_ref.write("# Agents, Mean In-deg, Men Sim, Std In-Deg, Std Sim, Connections\n")
        d_count = len(deg_att_data)
        sm_count = len(sim_att_data)
        if d_count > 0 and sm_count > 0:
            d_avg = sum(deg_att_data)/d_count
            sm_avg = sum(sim_att_data)/sm_count

            d_std = np.std(deg_att_data)
            sm_std = np.std(sim_att_data)
            f_ref.write("{}, {}, {}, {}, {}, {}\n"
                        .format(tot_nodes, d_avg, sm_avg, d_std, sm_std, d_count))
        f_ref.close()

# Create start_node_num, initially 4, each node is pointing to
# the next node in a loop to ensure the graph is connected and
# all four initial nodes have an in-degree
def setup():
    n = []
    for i in range(0, start_node_num):
        starter_node = sna_model.create_rnd_node()
        coefficient = i / start_node_num + 1 / (2 + start_node_num)
        print("word metric coefficient =", coefficient)
        starter_node.set_word_metric(coefficient)
        n.append(starter_node)
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
    good_match = sna_model.get_good_match(new_node, selection_mult)
    g.add_edge(new_node.get_name(), good_match.get_name())
    parent_match = sna_model.get_good_match(new_node, selection_mult)
    g.add_edge(parent_match.get_name(), new_node.get_name())

    good_match.set_in_degree(g.in_degree(good_match.get_name()))
    new_node.set_in_degree(g.in_degree(new_node.get_name()))
    parent_match.set_in_degree(g.in_degree(parent_match.get_name()))
    sna_model.update_graph_totals()


# This function is used to update the network

def modify_graph(num_of_nodes):
    global removals
    global old_tgt_skipped
    global edge_adds
    global new_nodes_skipped
    global tot_mods
    all_nodes = sna_model.get_nodes()
    keys = list(all_nodes.keys())
    node_mod_cnt = 0

    while node_mod_cnt < num_of_nodes:
        tot_mods += 1
        node_mod_cnt += 1
        k = random.choice(keys)
        source_node = all_nodes[k]
        # get worst match of source node
        edges = g.out_edges([source_node.get_name()])
        lst_to_check = []
        for e in edges:
            lst_to_check.append(all_nodes[e[1]])

        old_target_node = sna_model.get_least_sim_from_lst(source_node, lst_to_check)
        if old_target_node is None:
            print("target node removed skipped", old_tgt_skipped)
            old_tgt_skipped += 1
            continue

        old_tgt_in_degree = g.in_degree(old_target_node.get_name())

        # if old_tgt_in_degree is too low, don't get a new match
        # instead, get a new parent for the old target and remove edge
        new_match = None
        if old_tgt_in_degree > 1:
            new_match = sna_model.get_better_match(source_node, old_target_node, lst_to_check)
            if new_match is None:
                print("new_nodes_skipped {}, total modified {}, cnt this run {}"
                      .format(new_nodes_skipped, tot_mods, node_mod_cnt))
                new_nodes_skipped += 1
                continue
            g.add_edge(source_node.get_name(), new_match.get_name())
            new_match_degree_in = g.in_degree(new_match.get_name())
            new_match.set_in_degree(new_match_degree_in)
        else:
            parent_match = sna_model.get_good_match(old_target_node, selection_mult)
            g.add_edge(parent_match.get_name(), old_target_node.get_name())
        g.remove_edge(source_node.get_name(), old_target_node.get_name())

        removals += 1
        edge_adds += 1

        old_tgt_degree_in = g.in_degree(old_target_node.get_name())
        old_target_node.set_in_degree(old_tgt_degree_in)

        sna_model.update_graph_totals()


def do_community_detection():
    community_lst = nx.community.louvain_communities(g, resolution=res, seed=1234)
    sna_model.update_communities(community_lst)


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

print("4. Match Selection Multiplier (default 20")
try:
    selection_mult = int(input())
except ValueError:
    selection_mult = 20

print("4. Do run modifications? (default 0, > 0 is the number of runs)")
try:
    do_run_modifications = int(input())
except ValueError:
    do_run_modifications = 0


print("5. Modularity Resolution (1 default)")
try:
    res = float(input())
except ValueError:
    print("Resolution default to 1")
    res = 1

print("6. Attachment Probability Logging? (t or f, f default)")
l_val = input()
if l_val == 't':
    do_att_prob_logging = True
else:
    do_att_prob_logging = False

g = nx.DiGraph()
sna_model = ag.SNA_Model(do_att_prob_logging)

setup()
go()

if export_edge_table_flag:
    export_graph("org_")

h = None
# if do_run_modifications > 0:
#     h = chart.Histo()

original_list = sna_model.get_in_degree_lst()[:]
do_community_detection()
edge_changes_per_update = tot_nodes * .05
community_enum_for_graph = []
for i in range(do_run_modifications):
    modify_graph(edge_changes_per_update)
    print("--- run number: ", i, " ---")
    do_community_detection()
    # in_degree_data = sna_model.get_in_degree_lst()
    # h.update_plot(in_degree_data, community_enum_for_graph)
    fileNumber = i + 1
    # if i % 10 == 0:
    #     print("run number: ", i)

if export_graph_metrics_flag:
    export_graph_metrics()
    export_run_data()

print("start network = ", original_list)
print("end network = ", sna_model.get_in_degree_lst())
if export_edge_table_flag:
    export_graph("fin_")

# if do_run_modifications == 0:
#     h = chart.Histo()
# h.final_plot(sna_model.get_in_degree_lst(), community_enum_for_graph)
print("tot mods: {}, rm: {}, add:{}, old_sk: {}, new_sk: {}"
      .format(tot_mods, removals, edge_adds, old_tgt_skipped, new_nodes_skipped))
