import random


class Agent:
    def __init__(self, name, in_degree, word_metric, interaction_score):
        self.name = name
        self.in_degree = in_degree
        self.word_metric = word_metric
        self.interaction_score = interaction_score

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

    def get_interaction_score(self):
        return self.interaction_score

    # interaction will be a combination of view, like and share on a
    # scale from 0-10.  0 was user passed, i.e. no click
    def set_interaction_score(self, interaction_score):
        self.interaction_score = interaction_score


    def get_name(self):
        return self.name

    def __str__(self):
        return ("N: {}, D: {}, W: {}"
                .format(self.name, self.in_degree, self.word_metric))


class SNA_Model:

    def __init__(self):
        self.count = 0
        self.nodes = {}
        self.tot_in_degrees = 0
        self.word_metric_rng = 100
        self.match_threshold = .25
        self.tot_word_metric = 0
        self.tot_interaction_score = 0
        self.interaction_score_rng = 10

    def update_graph_totals(self):
        tot = 0
        int_score = 0
        keys = list(self.nodes.keys())
        for n in keys:
            tot += self.nodes[n].get_in_degree()
            int_score += self.nodes[n].get_interaction_score()
        self.tot_in_degrees = tot
        self.tot_interaction_score = len(keys) * int_score
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
        return (1 - abs(score1 - score2))/self.tot_word_metric

    def get_interaction_score_prob(self, node):
        return node.get_interaction_score() / self.tot_interaction_score

    # get a parent, this choice will be from similarity, right now
    # it is random
    def get_parent_for_new_node(self, node):
        keys = list(self.nodes.keys())
        keys.remove(node.get_name())
        min_diff = self.word_metric_rng
        best_key = None
        for k in keys:
            diff = abs(node.get_word_metric() - self.nodes[k].get_word_metric())
            if diff <= min_diff:
                min_diff = diff
                best_key = k
        return self.nodes[best_key]

    # this is for the recommended nodes (target nodes). Implement random activation,
    # this might prove to be too slow.
    def get_good_match(self, node_to_match, weights=(.3, .3, .4)):
        keys = list(self.nodes.keys())
        # picks nodes randomly and get attachment prob to test for selection
        # using the interactions score
        cnt = 0
        while True or cnt > 100000:
            k = random.choice(keys)
            if k != node_to_match.get_name():
                test_node = self.nodes[k]
                prob = self.get_node_att_prob(test_node)
                sim = self.get_node_similarity_prob(node_to_match, test_node)
                interaction = self.get_interaction_score_prob(test_node)
                roll = random.random()
                # these percentages (.3, .3, .34) would be interesting
                # to adjust for different results
                prob = weights[0]*prob + weights[1]*sim + weights[2]*interaction
                if prob >= roll:
                    return self.nodes[k]
                cnt += 1

    def get_better_match(self, node_to_match, old_target_node):
        keys = list(self.nodes.keys())
        # picks nodes randomly and get attachment prob to test for selection
        # using the interactions score
        cnt = 0
        while True or cnt > 100000:
            k = random.choice(keys)
            if k != node_to_match.get_name():
                test_node = self.nodes[k]
                test_sim = self.get_node_similarity_prob(node_to_match, test_node)
                test_interaction = self.get_interaction_score_prob(test_node)
                old_sim = self.get_node_similarity_prob(node_to_match, old_target_node)
                old_interaction = self.get_interaction_score_prob(old_target_node)
                # to adjust for different results
                test_score = 0.5 * test_sim + 0.5 * test_interaction
                old_score = 0.5 * old_sim + 0.5 * old_interaction
                if test_score >= old_score:
                    return self.nodes[k]
                cnt += 1

    def create_rnd_node(self):
        name = self.count
        in_degree = 0
        word_score = random.randint(0, self.word_metric_rng)
        interaction_score = random.randint(0, self.interaction_score_rng)
        node = Agent(name, in_degree, word_score, interaction_score)
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
