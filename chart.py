import time
import matplotlib.pyplot as plt
import numpy as np
# https://www.geeksforgeeks.org/how-to-update-a-plot-on-same-figure-during-the-loop/
# https://stackoverflow.com/questions/7694298/how-to-make-a-log-log-histogram-in-python
# Create a random number generator with a fixed seed for reproducibility

class Histo:
    def __init__(self):
        self.n_bins = 5
        plt.ion()
        self.fig, self.degAx = plt.subplots(1, 1, sharey=True, tight_layout=True)


    def update_plot(self, data):
        self.degAx.cla()
        self.degAx.set_xlabel("Log2(Node In-Degree)")
        self.degAx.set_ylabel("Log2(Node Count)")
        plt.title("In-degree/Word Similarity/Interaction")
        self.degAx.hist(np.log2(data), log=True, bins=self.n_bins)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def final_plot(self, data):
        self.degAx.cla()
        self.degAx.set_xlabel("Log2(Node In-Degree)")
        self.degAx.set_ylabel("Log2(Node Count)")
        plt.title("In-degree/Word Similarity/Interaction")
        self.degAx.hist(np.log2(data), log=True, bins=self.n_bins)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.show(block=True)


# h = Histo()
# rng = np.random.default_rng(19680801)
# for i in range(5):
#     data = rng.standard_normal(1000)
#     h.update_plot(data)
#     time.sleep(1)
