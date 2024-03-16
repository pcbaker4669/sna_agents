import random


class Agent:
    def __init__(self, name, interactions, similar_words, tick=0):
        self.name = name
        self.interactions = interactions
        self.similar_words = similar_words
        self.refresh_date = tick

    def update_node_interaction(self, in_degree, tick=None):
        self.interactions = in_degree
        if tick is not None:
            self.refresh_date = tick

    def get_name(self):
        return self.name

    def get_name_and_scores(self):
        return "N: {}, I: {}, W: {}, T: {}".format(self.name, self.interactions,
                                                   self.similar_words, self.refresh_date)

    # G.add_nodes_from([('person1', {'name': 'John Doe', 'age': 40})])
    def get_node_for_graph(self):
        node = {'name': self.name,
                'interactions': self.interactions,
                'similar_words': self.similar_words}
        return node

    # This is for parent node, find the match based on similar words
    def calc_compare_type(self, other):
        return abs(self.similar_words - other.similar_words)

    # this is to find the most popular video
    def get_interactions(self):
        return self.interactions

    def get_refresh_date(self):
        return self.refresh_date


class CC_Model:

    def __init__(self, refresh_threshold=3, min_interactions=2, score_rng=10):
        self.count = 0
        # used in get most popular node, when creating a node, the new
        # node's edge points to one node that is above average and similar
        # 2nd edge points to most similar
        self.interactions_avg = 0
        # Current highest interactions for a node
        self.interactions_max = 0
        # the node can sit this many ticks before it can be stale
        self.refresh_threshold = refresh_threshold
        # the node must have at least this many interactions before being stale
        self.min_interactions = min_interactions
        self.nodes = []
        # score range is for similarity range, 0-10 is default
        self.score_rng = score_rng
        self.removals = 0
        self.skips = 0
        self.worse_edges = 0
        self.worse_skips = 0

    def reset(self):
        self.count = 0
        self.interactions_avg = 0
        self.nodes = []

    def get_node_by_name(self, name):
        for n in self.nodes:
            if n.get_name() == name:
                return n

    def get_count(self):
        return self.count

    def get_nodes(self):
        return self.nodes

    def get_worse_match_nodes(self, edges):
        # 0 is the best match, no difference in words
        worse_match_node_val = 0
        avg = 0
        u = None
        v = None
        score = self.score_rng
        for e in edges:
            n = self.get_node_by_name(e[0])
            m = self.get_node_by_name(e[1])
            score = n.calc_compare_type(m)
            avg += score
            if worse_match_node_val >= score:
                u = m
                v = n
                worse_match_node_val = score
        #print("avg = ", avg/len(edges))
        if u is not None and v is not None:
            self.worse_edges += 1
            #print("worse match is u={} and v={} score = {}".format(u.get_name(), v.get_name(), score))
        else:
            self.worse_skips += 1
            #print("no worst matches found")
        return u, v, worse_match_node_val

    def get_stale_node(self):
        stalest_node_val = self.count
        stalest_node = None
        for n in self.nodes:
            if self.interactions_avg >= n.get_interactions():
                if stalest_node_val <= n.get_refresh_date():
                    stalest_node_val = n.get_refresh_date()
                    stalest_node = n
        if stalest_node is not None:
            self.removals += 1
        else:
            self.skips += 1
        return stalest_node

    def update_interactions_avg(self):
        val = 0
        refresh_val = 0
        max_interaction = 0
        for n in self.nodes:
            if n.get_interactions() > max_interaction:
                max_interaction = n.get_interactions()
            val += n.get_interactions()
            refresh_val += n.get_refresh_date()
        self.interactions_avg = val / len(self.nodes)
        self.refresh_threshold = refresh_val / len(self.nodes)
        self.interactions_max = max_interaction

    def get_parent_match(self, node):
        # do comparison based on "node", but don't pick yourself
        tmp_lst = self.nodes[:]
        tmp_lst.remove(node)
        best_node = None
        best_score = self.interactions_max
        for n in tmp_lst:
            score = n.calc_compare_type(node)
            if score <= best_score:
                best_score = score
                best_node = n
        if best_node is None:
            best_node = random.choice(tmp_lst)
        return best_node

    def get_similar_match(self, node, node_parent, num=2):
        # do comparison based on "node", but don't pick yourself
        tmp_lst = self.nodes[:]
        # don't pick yourself of your parent
        tmp_lst.remove(node)
        tmp_lst.remove(node_parent)

        best_arr = []
        for i in range(0, num):
            best_node = None
            best_score = self.score_rng
            for n in tmp_lst:
                score = n.calc_compare_type(node)
                if score <= best_score:
                    best_score = score
                    best_node = n
            if best_node is not None:
                best_arr.append(best_node)
                tmp_lst.remove(best_node)
        return best_arr

    def get_popular_matches(self, node, node_parent=None, num=1):
        tmp_lst = self.nodes[:]
        # don't pick yourself of your parent
        tmp_lst.remove(node)
        if node_parent is not None:
            tmp_lst.remove(node_parent)
        best_arr = []
        for i in range(0, num):
            best_node = None
            best_score = self.score_rng
            for n in tmp_lst:
                if n.get_interactions() >= self.interactions_avg:
                    score = n.calc_compare_type(node)
                    if score < best_score:
                        best_score = score
                        best_node = n
            if best_node is not None:
                best_arr.append(best_node)
                tmp_lst.remove(best_node)

        return best_arr

    # when adding an edge, one node will be picked at random
    def get_rnd_node(self):
        node = random.choice(self.nodes)
        return node

    def create_rnd_node(self):
        self.count += 1
        name = self.count
        interactions = 0
        similar_words = random.randint(0, self.score_rng)
        node = Agent(name, interactions, similar_words, self.count)
        self.nodes.append(node)
        self.update_interactions_avg()
        return node

    # starter nodes have interaction scores

    def get_node_name_lst(self):
        lst = []
        for n in self.nodes:
            lst.append(n.get_name())
        return lst

    def get_node_name_score_lst(self):
        lst = []
        for n in self.nodes:
            lst.append(n.get_name_and_scores())
        return lst

    def get_skips_and_removal_num(self):
        return ("skips={}, removals={}, worse edge skips={}, worse edge removes={}"
                .format(self.skips, self.removals, self.worse_skips, self.worse_edges))
