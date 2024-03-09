# 1. Objectives
# Primary Objective: To model and analyze how clustering coefficients
# evolve in a social network and how friends-of-friends connections
# contribute to the formation of tight-knit communities over time.
# Secondary Objectives: To identify key factors influencing high
# clustering coefficients and to simulate various scenarios to understand
# their impacts on social network dynamics.
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
from tkinter import messagebox
import random
import sys
import g_utils

btnWt = 20
lblWt = 10
compFrmHt = 100
kVal = 25

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

componentFrm = tk.Frame(root, height=compFrmHt)
componentFrm.pack(padx=10, pady=10, side="bottom")

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

g = nx.DiGraph()


def draw_graph():

    node_val_lbl.config(text=f"{len(g.nodes)}")
    edge_val_lbl.config(text=f"{len(g.edges)}")

    nx.draw_networkx(g, pos=nx.spring_layout(g, kVal), alpha=1,
                     with_labels=True, node_size=100, node_color="green")
    if len(g.edges) > 3:
        tra_cnt = nx.transitivity(g)
        print("tri_cnt = ", tra_cnt)
        if tra_cnt is not None:
            tran_val_lbl.config(text="{:.4f}".format(tra_cnt))
            clus = nx.clustering(g)
            print("clustering = ", clus)

    canvas.draw()


def reset_canvas():
    plt.clf()
    plt.gca().set_facecolor("grey")
    fig.set_facecolor("black")


def setup():
    reset_canvas()
    g.clear()
    g.add_edge(1, random.choice(mlist))
    plt.gca().set_facecolor("grey")
    fig.set_facecolor("black")
    draw_graph()


mlist = range(2, 99)
setup()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=True)


def add_node_to_graph():
    reset_canvas()
    # get node from graph and randomly select
    # eventually make less random by attributes
    nlist = list(g.nodes)
    g.add_edge(random.choice(nlist), random.choice(mlist))
    draw_graph()


def add_edge_to_graph():
    reset_canvas()
    # get node from graph and randomly select
    # eventually make less random by attributes
    n1, n2 = g_utils.pick_2_unique_nodes(g)
    if n1 is None or n2 is None:
        print("did not create an edge")
        return
    print("Adding edge ({}, {})".format(n1, n2))
    g.add_edge(n1, n2)
    draw_graph()


root.mainloop()
