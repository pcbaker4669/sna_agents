import time
import matplotlib.pyplot as plt
import numpy as np
# https://www.geeksforgeeks.org/how-to-update-a-plot-on-same-figure-during-the-loop/
# https://stackoverflow.com/questions/7694298/how-to-make-a-log-log-histogram-in-python
# Create a random number generator with a fixed seed for reproducibility

class Histo:
    def __init__(self, d_bins=5, mod_bins=5):
        self.n_bins = 5
        plt.ion()
        self.fig, self.ax = plt.subplots(1, 2, sharey=True, tight_layout=True)


    def update_plot(self, data):
        self.ax[0].cla()
        self.ax[0].set_xlabel("Log2(Node In-Degree)")
        self.ax[0].set_ylabel("Log2(Node Count)")
        plt.title("In-degree/Word Similarity/Interaction")
        self.ax[0].hist(np.log2(data), log=True, bins=self.n_bins)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

        # this will be modularity
        self.ax[1].cla()
        self.ax[1].set_xlabel("Community Group")
        self.ax[1].set_ylabel("Count)")
        plt.title("Community Members")
        self.ax[1].hist(np.log2(data), log=True, bins=self.n_bins)
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

    def final_plot(self, data):
        self.update_plot(data)
        plt.show(block=True)


# h = Histo()
# rng = np.random.default_rng(19680801)
# for i in range(5):
#     data = rng.standard_normal(1000)
#     h.update_plot(data)
#     time.sleep(1)
