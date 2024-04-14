import networkx as nx
import matplotlib.pyplot as plt

class GraphNet:
    def __init__(self, g):
        self.g = g
        plt.ion()
        self.fig, self.ax = plt.subplots(1, 1)

    def display_graph(self):
        #self.ax.cla()
        nx.draw_networkx(self.g)
        self.ax = plt.gca()
        self.ax.margins(0.20)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def freeze_plot(self):
        plt.show(block=True)
