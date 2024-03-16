# 1. Objectives
# Primary Objective: To model a social network recommendation
# system similar to YouTube where network structure is a hybrid
# scale-free network
import networkx as nx
import agent as ag
import random as rnd

start_node_num = 4
tot_nodes = 200

log_list = []
nodes_per_step = 4


def export_graph():
    edges = g.edges
    f_ref = open(f"output_{tot_nodes}_3.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


g = nx.DiGraph()
cc_model = ag.CC_Model()

def setup():
    n = []
    for i in range(0, start_node_num):
        n.append(cc_model.create_rnd_node())
        g.add_node(n[i].get_name())

    for i in range(1, start_node_num):
        g.add_edge(n[i-1].get_name(), n[i].get_name())

    for i in range(0, start_node_num):
        n[i].update_node_interaction(g.in_degree(n[i].get_name()), cc_model.get_count())


def add_node_to_graph():
    n_new = cc_model.create_rnd_node()
    g.add_node(n_new.get_name())
    #print("new is: ", n_new.get_name())
    # nrp will be the parent that picks you based on similar words
    nrp = cc_model.get_parent_match(n_new)

    # nr2 and nr3 will be recs that your video provides
    # nr2 will be above average interactions and similar words
    #nr2_lst = cc_model.get_popular_matches(n_new, nrp, 1)

    # nr3 will be only based on similar words
    nr3_lst = cc_model.get_similar_match(n_new, nrp, 3)

    g.add_edge(nrp.get_name(), n_new.get_name())
    # for n in nr2_lst:
    #     g.add_edge(n_new.get_name(), n.get_name())

    for n in nr3_lst:
        g.add_edge(n_new.get_name(), n.get_name())

    # remove node with oldest interactions
    stalest_node = cc_model.get_stale_node()
    remove_edge_by_node(stalest_node)
    edge_lst = list(g.edges)

    u, v, s = cc_model.get_worse_match_nodes(edge_lst)
    if u is not None and v is not None:
        if (u.get_name(), v.get_name()) in edge_lst:
            g.remove_edge(u.get_name(), v.get_name())
            #print("1. remove an edge {}, {}, score = {}".format(u.get_name(), v.get_name(), s))
        if (v.get_name(), u.get_name()) in edge_lst:
            g.remove_edge(v.get_name(), u.get_name())
            #print("2. removed an edge {}, {}, score = {}".format(v.get_name(), u.get_name(), s))
    else:
        pass
        # print("didn't find a worse edge: ", edge_lst)

    for n in cc_model.get_nodes():
        n.update_node_interaction(g.in_degree(n.get_name()), cc_model.get_count())



def remove_edge_by_node(node):
    if node is not None:
        node_name = node.get_name()
        edges_in = list(g.in_edges(node_name))
        if len(edges_in) > 0:
            u, v = rnd.choice(edges_in)
            g.remove_edge(u, v)
            node.update_node_interaction(g.in_degree(node_name), cc_model.get_count())

def go():
    # Add first node to graph

    while cc_model.get_count() <= tot_nodes:
        add_node_to_graph()
        node_cnt = len(g.nodes)
        print("node cnt = ", node_cnt)

setup()
go()
print("skips and removals: ", cc_model.get_skips_and_removal_num())
export_graph()
