import random
import numpy as np

class Agent:
    def __init__(self, name, in_degree, word_metric):
        self.name = name
        self.in_degree = in_degree
        self.word_metric = word_metric

    def set_in_degree(self, in_degree):
        self.in_degree = in_degree

    def get_in_degree(self):
        return self.in_degree

    def increment_in_degree(self):
        self.in_degree += 1

    def set_word_metric(self, score):
        self.word_metric = score

    def get_word_metric(self):
        return self.word_metric

    def sort_priority(self):
        return self.word_metric

    def get_name(self):
        return self.name

    def __str__(self):
        return ("N: {}, In-D: {}, W-M: {}"
                .format(self.name, self.in_degree, self.word_metric))


class SNA_Model:

    def __init__(self, pool_size):
        self.count = 0
        self.nodes = {}
        self.tot_in_degrees = 0
        self.word_metric_rng = 1
        self.tot_word_metric = 0
        self.node_pool = []

    def create_node_pool(self, pool_size):
        for i in range(pool_size):
            node = self.create_rnd_node()
            self.node_pool.append(node)


    def update_graph_totals(self):
        tot = 0

        keys = list(self.nodes.keys())
        for n in keys:
            tot += self.nodes[n].get_in_degree()
        self.tot_in_degrees = tot

        # we want the word metric denominator to grow similar to tot_in_degrees
        # so that the probabilities are similar when selecting a node
        self.tot_word_metric = len(keys) * (self.word_metric_rng/2.0)

    def get_count(self):
        return self.count

    def get_nodes(self):
        return self.nodes

    def get_node_att_prob(self, node):
        return node.get_in_degree() / self.tot_in_degrees

    #
    def get_node_similarity_prob(self, created_node, test_node):
        score1 = created_node.get_word_metric()
        score2 = test_node.get_word_metric()
        return (self.word_metric_rng - abs(score1 - score2))/self.tot_word_metric



    # this is for the recommended nodes (target nodes). Implement random activation,
    # this might prove to be too slow.
    def get_good_match(self, node_to_match, in_degree_wt, similarity_wt):

        # picks nodes randomly and get attachment prob to test for selection
        # using the interactions score
        cnt = 0

        while True or cnt > 1000000:
            k = random.choice(self.node_pool)
            if k != node_to_match.get_name():
                test_node = self.nodes[k]
                prob = self.get_node_att_prob(test_node)
                sim = self.get_node_similarity_prob(node_to_match, test_node)

                roll = random.random()
                # these percentages (.3, .3, .34) would be interesting
                # to adjust for different results
                prob = (in_degree_wt*prob + similarity_wt*sim)
                if prob >= roll:
                    return self.nodes[k]
                cnt += 1

    def create_start_node(self, mean, sigma):
        name = self.count
        in_degree = 0
        word_score = np.random.normal(mean, sigma)
        node = Agent(name, in_degree, word_score)
        keys = self.nodes.keys()
        if name not in keys:
            self.nodes[name] = node
        else:
            print("error: node already exits {}".format(name))
        self.count += 1
        return node

    def create_rnd_node(self):
        name = self.count
        in_degree = 0
        word_score = random.random()
        node = Agent(name, in_degree, word_score)
        keys = self.nodes.keys()
        if name not in keys:
            self.nodes[name] = node
        else:
            print("error: node already exits {}".format(name))
        self.count += 1
        return node

    def get_nodes_sorted_by_metric(self):
        keys = self.nodes.keys()
        lst = []
        for k in keys:
            lst.append(self.nodes[k])
        lst = sorted(lst, key=lambda x: x.get_word_metric())
        return lst

    def get_in_degree_lst(self):
        keys = self.nodes.keys()
        lst = []
        for k in keys:
            lst.append(self.nodes[k].get_in_degree())
        return lst

    def __str__(self):
        s = ''
        keys = self.nodes.keys()
        for i in keys:
            s += "(" + str(self.nodes[i].get_name()) + ":" + str(self.nodes[i].get_in_degree()) + ")"
        return s
