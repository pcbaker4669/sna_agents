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
        print("node = ", node)
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

    def __init__(self):
        self.count = 0
        self.interactions_avg = 0
        self.nodes = []

    def reset(self):
        self.count = 0
        self.interactions_avg = 0
        self.nodes = []

    def get_count(self):
        return self.count

    def get_stale_node(self):
        stalest_node_val = self.count
        stalest_node = None
        for n in self.nodes:
            if self.interactions_avg >= n.get_interactions() >= 1:
                if stalest_node_val >= n.get_refresh_date():
                    stalest_node_val = n.get_refresh_date()
                    stalest_node = n
        if stalest_node is not None:
            print("stale: {}, date: {}, inter: {} "
                  .format(stalest_node.get_name(),
                          stalest_node.get_refresh_date(),
                          stalest_node.get_interactions()))
        else:
            print("no stale nodes found")
        return stalest_node

    def update_interactions_avg(self):
        val = 0
        for n in self.nodes:
            val += n.get_interactions()
        self.interactions_avg = val / len(self.nodes)
        print("average interaction = ", self.interactions_avg)

    def get_closest_match(self, node, exclude_nodes=()):
        # do comparison based on "node", but don't pick yourself
        tmp_lst = self.nodes[:]
        tmp_lst.remove(node)
        for exc in exclude_nodes:
            try:
                tmp_lst.remove(exc)
            except ValueError:
                print("tried to remove something not in list")
        best_node = None
        best_score = 10
        for n in tmp_lst:
            score = n.calc_compare_type(node)
            if score <= best_score:
                best_score = score
                best_node = n
        return best_node

    def get_most_popular_match(self, node, exclude_nodes=()):
        tmp_lst = self.nodes[:]
        tmp_lst.remove(node)
        for exc in exclude_nodes:
            tmp_lst.remove(exc)
        best_node = None
        best_score = 10
        for n in tmp_lst:
            if n.get_interactions() >= self.interactions_avg:
                score = n.calc_compare_type(node)
                if score < best_score:
                    best_score = score
                    best_node = n
        return best_node

    # when adding an edge, one node will be picked at random
    def get_rnd_node(self):
        node = random.choice(self.nodes)
        return node

    def create_rnd_node(self):
        self.count += 1
        name = self.count
        interactions = 0
        similar_words = random.randint(0, 10)
        node = Agent(name, interactions, similar_words, self.count)
        self.nodes.append(node)
        self.update_interactions_avg()
        return node

    # starter nodes have interaction scores
    def create_starter_node(self):
        self.count += 1
        name = self.count
        similar_words = random.randint(0, 10)
        # this way we know n1 interactions > n2 interactions etc for initial
        # edge selections (3 nodes and 2 edges)
        interactions = 0
        node = Agent(name, interactions, similar_words, self.count)
        self.nodes.append(node)
        self.update_interactions_avg()
        return node

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
