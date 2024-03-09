import networkx as nx
import random


def pick_2_unique_nodes(g):
    nlist = list(g.nodes)
    elist = list(g.edges)
    n1 = random.choice(nlist)
    n2 = random.choice(nlist)

    while n1 == n2 or (n1, n2) in g.edges:
        if (n1, n2) in elist:
            elist.remove((n1, n2))
            if len(elist) < 1:
                print("exiting, no unconnected nodes")
                return None, None

        n1 = random.choice(nlist)
        n2 = random.choice(nlist)

    return n1, n2
