import random
import numpy as np

random.seed(123)


class Agent:
    def __init__(self, name, in_degree, word_metric):
        self.name = name
        self.in_degree = in_degree
        self.word_metric = word_metric
        self.community = -1

    def set_community(self, community):
        self.community = community

    def get_community(self):
        return self.community

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

    def __init__(self, logging=False):
        self.count = 0
        self.nodes = {}
        self.tot_in_degrees = 0
        self.word_metric_rng = 1
        self.tot_word_metric = 0
        self.community_groups_means = {}
        self.community_groups_std = {}
        self.community_groups_cnt = {}
        self.mean_std_dev_of_com_by_run = []
        self.in_degree_att_probs_log = []
        self.wm_sim_att_probs_log = []
        self.logging = logging

    def update_graph_totals(self):
        tot = 0
        keys = list(self.nodes.keys())
        for n in keys:
            tot += self.nodes[n].get_in_degree()
        self.tot_in_degrees = tot

        # we want the word metric denominator to grow similar to tot_in_degrees
        # so that the probabilities are similar when selecting a node
        self.tot_word_metric = len(keys) * (self.word_metric_rng / 2.0)

    def get_count(self):
        return self.count

    def get_nodes(self):
        return self.nodes

    def get_node_att_prob(self, node):
        val = node.get_in_degree() / self.tot_in_degrees
        if self.logging:
            self.in_degree_att_probs_log.append(val)
        return val

    #
    def get_node_similarity_prob(self, created_node, test_node):
        score1 = created_node.get_word_metric()
        score2 = test_node.get_word_metric()
        val = (self.word_metric_rng - abs(score1 - score2)) / self.tot_word_metric
        if self.logging:
            self.wm_sim_att_probs_log.append(val)
        return val

    # get a parent, set tries to be some number passed in (later)
    def get_good_match(self, node_to_match, selection_mult):
        keys = list(self.nodes.keys())
        keys.remove(node_to_match.get_name())
        tries = selection_mult * len(keys)
        current_key = random.choice(keys)
        current_node = self.nodes[current_key]
        cnt = 0
        while cnt < tries:
            cnt += 1
            test_key = random.choice(keys)
            test_node = self.nodes[test_key]
            diff_test = (node_to_match.get_word_metric() -
                         test_node.get_word_metric())
            diff_current = (node_to_match.get_word_metric() -
                            current_node.get_word_metric())
            if abs(diff_test) < abs(diff_current):
                test_prob = self.get_node_att_prob(test_node)
                roll = random.random()
                if test_prob >= roll:
                    current_node = test_node
        return current_node


    def get_least_sim_from_lst(self, node_to_match, lst_of_nodes):
        worst_score = 0
        node_to_return = None
        for n in lst_of_nodes:
            test_sim = abs(node_to_match.get_word_metric() - n.get_word_metric())
            if test_sim >= worst_score:
                worst_score = test_sim
                node_to_return = n
        return node_to_return

    def get_better_match(self, node_to_match, old_target_node, exclude_lst=()):
        keys = list(self.nodes.keys())
        keys.remove(node_to_match.get_name())
        keys.remove(old_target_node.get_name())
        # ex
        for e in exclude_lst:
            if e.get_name() in keys:
                keys.remove(e.get_name())
        for i in range(500):
            random.shuffle(keys)
            for k in keys:
                test_node = self.nodes[k]
                diff_new = (node_to_match.get_word_metric() -
                            test_node.get_word_metric())
                diff_old = (node_to_match.get_word_metric() -
                            old_target_node.get_word_metric())
                if abs(diff_new) < abs(diff_old):
                    test_prob = self.get_node_att_prob(test_node)
                    roll = random.random()
                    if test_prob >= roll:
                        return self.nodes[k]
        return None

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

    def update_communities(self, com_lst):
        com_group = 0
        self.community_groups_means[com_group] = {}
        self.community_groups_std[com_group] = {}
        std_per_run_for_group = []
        # each com_lst is a list of node names in a community
        # go through each list, find the node and assign it a
        # community number list 0 is comm 0, etc
        for com in com_lst:
            word_metrics_for_com = []
            for idx in com:
                self.nodes[idx].set_community(com_group)
                word_metrics_for_com.append(self.nodes[idx].get_word_metric())

            self.community_groups_cnt[com_group] = len(com)
            self.community_groups_means[com_group] = (
                    sum(word_metrics_for_com) / len(com))
            self.community_groups_std[com_group] = np.std(word_metrics_for_com)

            com_group += 1
        val = sum(self.community_groups_std.values()) / len(self.community_groups_std.keys())
        self.mean_std_dev_of_com_by_run.append(val)
        print("std or this run: ", val)

    def get_mean_std_dev_of_com_by_run(self):
        return self.mean_std_dev_of_com_by_run

    def get_community_run_metrics_for_each_all_groups(self):
        stat_strs = []
        for idx in range(len(self.community_groups_cnt)):
            cnt = self.community_groups_cnt[idx]
            mean = self.community_groups_means[idx]
            std = self.community_groups_std[idx]
            s = "{}, {}, {:.6f}, {:.6f}\n".format(idx, cnt, mean, std)
            stat_strs.append(s)
        return stat_strs

    def get_community_means(self):
        return self.community_groups_means

    def get_community_std(self):
        return self.community_groups_std

    def get_community_cnt(self):
        return self.community_groups_cnt

    def get_in_degree_att_probs_log(self):
        return self.in_degree_att_probs_log

    def get_wm_sim_att_probs_log(self):
        return self.wm_sim_att_probs_log

    def __str__(self):
        s = ''
        keys = self.nodes.keys()
        for i in keys:
            s += "(" + str(self.nodes[i].get_name()) + ":" + str(self.nodes[i].get_in_degree()) + ")"
        return s
