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
import agent as ag

import random
import sys
import g_utils

btnWt = 20
lblWt = 10
compFrmHt = 100
kVal = 25
new_edges_per_new_node = 3

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg
)


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        sys.exit()


root = Tk()
root.title("cc agents")
root.protocol('WM_DELETE_WINDOW', on_closing)

fig = plt.figure(frameon=False, figsize=(5, 3), dpi=100)
canvas = FigureCanvasTkAgg(fig, root)

dataFrm = tk.Frame(root, width=100)
dataFrm.pack(padx=10, pady=10, side="right")

componentFrm = tk.Frame(root, height=compFrmHt)
componentFrm.pack(padx=10, pady=10, side="bottom")

# ----------------- Data Frame --------------------
listbox = Listbox(dataFrm, height=10,
                  width=15,
                  bg="grey",
                  activestyle='dotbox',
                  font="Helvetica",
                  fg="yellow")

lstLbl = Label(dataFrm, text="Clusters")

# pack the widgets
lstLbl.pack()
listbox.pack()

# ----------------- Button Frame -------------------
btnFrm = tk.Frame(componentFrm)
btnFrm.pack(padx=10, pady=10, side="right")
setupBtn = tk.Button(btnFrm, text="Setup", width=btnWt,
                     command=lambda: setup())
setupBtn.pack(side="top")
addNodeBtn = tk.Button(btnFrm, text="Add Node", width=btnWt,
                       command=lambda: add_node_to_graph())
addNodeBtn.pack(side="top")

addEdgeBtn = tk.Button(btnFrm, text="Add Edge", width=btnWt,
                       command=lambda: add_edge_to_graph())
addEdgeBtn.pack(side="bottom")

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
        #print("tri_cnt = ", tra_cnt)
        if tra_cnt is not None:
            tran_val_lbl.config(text="{:.4f}".format(tra_cnt))
            clus = nx.clustering(g)
            #print("clustering = ", clus)
            listbox.delete(0, END)
            keys = list(clus.keys())
            cnt = 1
            for k in keys:
                s = "{}, {:.4f}".format(k, clus[k])
                listbox.insert(cnt, s)
                cnt += 1

    canvas.draw()


def reset_canvas():
    plt.clf()
    plt.gca().set_facecolor("grey")
    fig.set_facecolor("black")


def setup():
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
    nrp = cc_model.get_closest_match(n_new)
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
    lst = cc_model.get_node_name_lst()
    print("list of nodes: ", lst)
    dlst = g.in_degree(lst)
    print("degrees: ", list(dlst))
    draw_graph()


def add_edge_to_graph():
    reset_canvas()
    # get node from graph and randomly select
    n2 = cc_model.get_rnd_node()
    # eventually make less random by attributes
    n1 = cc_model.get_rec_node(n2)
    if n1 is None:
        print("Can't add node in add_edge_to_graph")
        return
    print("Adding edge ({}, {})".format(n1.get_name(), n2.get_name()))
    g.add_edge(n1.get_name(), n2.get_name())
    draw_graph()


root.mainloop()
