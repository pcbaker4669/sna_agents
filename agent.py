import random


class Agent:
    def __init__(self, name, in_degree, content_score):
        self.name = name
        self.in_degree = in_degree
        self.content_score = content_score

    def set_in_degree(self, in_degree):
        self.in_degree = in_degree

    def get_in_degree(self):
        return self.in_degree

    def increment_in_degree(self):
        self.in_degree += 1

    def set_content_score(self, score):
        self.content_score = score

    def get_content_score(self):
        return self.content_score

    def get_name(self):
        return self.name

    def __str__(self):
        return ("N: {}, I: {}, C: {}"
                .format(self.name, self.in_degree, self.content_score))


class SNA_Model:

    def __init__(self):
        self.count = 0
        self.nodes = {}
        self.tot_in_degrees = 0
        self.content_score_rng = 100
        self.match_threshold = .25

    def update_graph_totals(self):
        tot = 0
        keys = list(self.nodes.keys())
        for n in keys:
            tot += self.nodes[n].get_in_degree()
        self.tot_in_degrees = tot

    def get_count(self):
        return self.count

    def get_nodes(self):
        return self.nodes

    def get_node_att_prob(self, node):
        return node.get_in_degree() / self.tot_in_degrees

    #
    def get_node_similarity_prob(self, created_node, test_node):
        score1 = created_node.get_content_score()
        score2 = test_node.get_content_score()
        return 1 - abs(score1 - score2)/self.content_score_rng


    # get a parent, this choice will be from similarity, right now
    # it is random
    def get_parent_for_new_node(self, node):
        keys = list(self.nodes.keys())
        keys.remove(node.get_name())
        min_diff = self.content_score_rng
        best_key = None
        for k in keys:
            diff = abs(node.get_content_score() - self.nodes[k].get_content_score())
            if diff <= min_diff:
                min_diff = diff
                best_key = k
        return self.nodes[best_key]

    # this is for the recommended nodes, the new node has interaction
    # zero and won't get picked.  Implement random activation, this
    # might prove to be too slow.
    def get_popular_match(self, node_to_match):

        keys = list(self.nodes.keys())
        # picks nodes randomly and get attachment prob to test for selection
        # using the interactions score
        cnt = 0
        while True or cnt > 100000:
            k = random.choice(keys)
            prob = int(self.get_node_att_prob(self.nodes[k]) * 100)
            roll = random.randint(0, 100)
            # print("> {}, node: {}, prob: {}, roll: {}".format(cnt, k, prob, roll))
            if prob >= roll:
                print(f"get_popular_match ran {cnt} attempts before finds a match")
                return self.nodes[k]
            cnt += 1

    def create_rnd_node(self):
        name = self.count
        interactions = 0
        content_score = random.randint(0, self.content_score_rng)
        node = Agent(name, interactions, content_score)
        keys = self.nodes.keys()
        if name not in keys:
            self.nodes[name] = node
        else:
            print("error: node already exits {}".format(name))
        self.count += 1
        return node

    def __str__(self):
        s = ''
        keys = self.nodes.keys()
        for i in keys:
            s += "(" + str(self.nodes[i].get_name()) + ":" + str(self.nodes[i].get_in_degree()) + ")"
        return s
