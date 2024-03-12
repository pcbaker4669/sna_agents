# 1. Objectives
# Primary Objective: To model and analyze how clustering
# evolves in a social network and how connections
# contribute to the formation of tight-knit communities over time.
# Secondary Objectives: To identify key factors influencing high
# clustering coefficients and to simulate various scenarios to understand
# their impacts on social network dynamics.
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import agent as ag
import ui
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)
import random as rnd
btnWt = 20
lblWt = 10
compFrmHt = 100
kVal = 25
new_edges_per_new_node = 3


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.quit()


def export_graph():
    edges = g.edges
    f_ref = open("output.csv", "w")
    f_ref.write("Source, Target, Link\n")
    for e in edges:
        f_ref.write("{}, {}, {}\n".format(e[0], e[1], "1"))
    f_ref.close()


root = Tk()
root.title("cc agents")
root.protocol('WM_DELETE_WINDOW', on_closing)

# Creating Menubar
menubar = Menu(root)

# Adding File Menu and commands
file = Menu(menubar, tearoff=0)
menubar.add_cascade(label='File', menu=file)
file.add_command(label='Export Graph', command=export_graph)
file.add_command(label='Export Agents', command=None)

# Adding Help Menu
help_ = Menu(menubar, tearoff=0)
menubar.add_cascade(label='Help', menu=help_)
help_.add_command(label='CC Agents', command=None)
help_.add_separator()

# display Menu
root.config(menu=menubar)

fig = plt.figure(frameon=False, figsize=(5, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, root)

tabControl = ttk.Notebook(root)
clusterTab = ttk.Frame(tabControl)
degreeTab = ttk.Frame(tabControl)
scoresTab = ttk.Frame(tabControl)

tabControl.add(clusterTab, text="Clustering")
tabControl.add(degreeTab, text="Degree")
tabControl.add(scoresTab, text="Scores")
tabControl.pack(side="right", padx=10, expand=1, fill="both")

componentFrm = tk.Frame(root, height=compFrmHt)
componentFrm.pack(padx=10, pady=10, side="bottom")

# ----------------- Notebook (tab1) --------------------
cluster_listbox = ui.make_lst_box(clusterTab, "Clustering: Node, C.C.")
degree_listbox = ui.make_lst_box(degreeTab, "Degree: Node, In-Degree")
score_listbox = ui.make_lst_box(scoresTab, "Scores: Node, Int, Wrds, Tck")

# ----------------- Button Frame -------------------
btnFrm = tk.Frame(componentFrm)
btnFrm.pack(padx=10, pady=10, side="right")
setupBtn = tk.Button(btnFrm, text="Setup", width=btnWt,
                     command=lambda: setup())
setupBtn.pack(side="top")
addNodeBtn = tk.Button(btnFrm, text="Step", width=btnWt,
                       command=lambda: add_node_to_graph())
addNodeBtn.pack(side="top")

# ----------------- Info Frame -------------------
infoFrm = tk.Frame(componentFrm)
infoFrm.pack(padx=10, pady=10, side="left")
node_lbl = tk.Label(infoFrm, text="Nodes:", width=lblWt)
node_lbl.pack(side="left")
node_val_lbl = tk.Label(infoFrm, text="2", width=lblWt)
node_val_lbl.pack(side="left")

edge_lbl = tk.Label(infoFrm, text="Edges:", width=lblWt)
edge_lbl.pack(side="left")
edge_val_lbl = tk.Label(infoFrm, text="1", width=lblWt)
edge_val_lbl.pack(side="left")

tran_lbl = tk.Label(infoFrm, text="Transitivity:", width=lblWt)
tran_lbl.pack(side="left")

tran_val_lbl = tk.Label(infoFrm, text="0", width=lblWt)
tran_val_lbl.pack(side="left")

cc_model = ag.CC_Model()

g = nx.DiGraph()


def draw_graph():
    node_val_lbl.config(text=f"{len(g.nodes)}")
    edge_val_lbl.config(text=f"{len(g.edges)}")

    nx.draw_networkx(g, pos=nx.spring_layout(g, kVal), alpha=1,
                     with_labels=True, node_size=100, node_color="green")
    if len(g.edges) > 3:
        tra_cnt = nx.transitivity(g)

        if tra_cnt is not None:
            tran_val_lbl.config(text="{:.4f}".format(tra_cnt))
            clus = nx.clustering(g)
            cluster_listbox.delete(0, END)
            keys = list(clus.keys())
            cnt = 1
            for k in keys:
                s = "N: {}, C.C. {:.4f}".format(k, clus[k])
                cluster_listbox.insert(cnt, s)
                cnt += 1
        # degree stuff
        lst = cc_model.get_node_name_lst()

        dlst = g.in_degree(lst)
        degree_listbox.delete(0, END)
        cnt = 1
        for d in dlst:
            s = "N: {}, In-D: {}".format(d[0], d[1])
            degree_listbox.insert(cnt, s)
            cnt += 1
        slst = cc_model.get_node_name_score_lst()
        score_listbox.delete(0, END)

        cnt = 1
        for s in slst:
            score_listbox.insert(cnt, s)
            cnt += 1


    canvas.draw()


def reset_canvas():
    plt.clf()
    plt.gca().set_facecolor("grey")
    fig.set_facecolor("black")


def setup():
    cc_model.reset()
    reset_canvas()
    g.clear()
    n1 = cc_model.create_starter_node()
    n2 = cc_model.create_starter_node()
    n3 = cc_model.create_starter_node()
    g.add_nodes_from([(n1.get_name(), n1.get_node_for_graph()),
                      (n2.get_name(), n2.get_node_for_graph()),
                      (n3.get_name(), n3.get_node_for_graph())])
    g.add_edge(n1.get_name(), n2.get_name())
    g.add_edge(n1.get_name(), n3.get_name())
    plt.gca().set_facecolor("grey")
    fig.set_facecolor("black")
    draw_graph()


setup()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)


def add_node_to_graph():
    reset_canvas()
    n_new = cc_model.create_rnd_node()
    # nrp will be the parent that picks you based on similar words
    nrp = cc_model.get_closest_match(n_new, [])
    # nr2 and nr3 will be recs that your video provides
    # nr2 will be above average interactions and similar words
    nr2 = cc_model.get_most_popular_match(n_new, [nrp])
    # nr3 will be only based on similar words
    nr3 = cc_model.get_closest_match(n_new, [nrp, nr2])
    g.add_nodes_from([(n_new.get_name(), n_new.get_node_for_graph())])
    g.add_edge(nrp.get_name(), n_new.get_name())
    print("parent to new: {} -> {}".format(nrp.get_name(), n_new.get_name()))
    g.add_edge(n_new.get_name(), nr2.get_name())
    print("new to rec1: {} -> {}".format(n_new.get_name(), nr2.get_name()))
    g.add_edge(n_new.get_name(), nr3.get_name())
    print("new to rec2: {} -> {}".format(n_new.get_name(), nr3.get_name()))
    n_new.update_node_interaction(g.in_degree(n_new.get_name()), cc_model.get_count())
    nr2.update_node_interaction(g.in_degree(nr2.get_name()), cc_model.get_count())
    nr3.update_node_interaction(g.in_degree(nr3.get_name()), cc_model.get_count())
    # remove old edge here (don't remove n_new
    stalest_node = cc_model.get_stale_node()
    # get edges from node (in only)
    if stalest_node is not None:
        stale_node_name = stalest_node.get_name()
        edges_in = list(g.in_edges(stale_node_name))
        if len(edges_in) > 0:
            print("edges in stalest node: ", edges_in)
            u, v = rnd.choice(edges_in)
            g.remove_edge(u, v)
            stalest_node.update_node_interaction(g.in_degree(stale_node_name))
            print("removing in edge from stalest node {}".format(
                  stalest_node.get_name()))

    else:
        print("there are no stale nodes yet")
    # select random edge and delete
    draw_graph()


root.mainloop()
